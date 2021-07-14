import logging
import typing as t
from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from api import schemas
from api.crud import game
from api.endpoints import get_db
from api.utils import auth

log = logging.getLogger(__name__)
router = APIRouter(tags=["Game Endpoints"], dependencies=[Depends(auth.JWTBearer())])

INITIAL_GAME = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


@router.get("/new")
async def new_game_create(request: Request) -> dict:
    """Make a new chess game and send link to game room."""
    user_id = await auth.JWTBearer().get_user_by_token(request)
    db = next(get_db())

    game_id = int(datetime.now().timestamp())
    new_game_obj = schemas.game.GameCreate(
        game_id=game_id,
        is_ongoing=True,
        winner_id=0,
        player_one_id=user_id,
        player_two_id=0,
        board=INITIAL_GAME,
    )
    game.create(db, obj_in=new_game_obj)

    return {"room": f"/game/{game_id}"}


class ChessNotifier:
    """Manages chess room sessions and members."""

    def __init__(self):
        self.connections: dict = defaultdict(dict)
        self.generator = self.get_notification_generator()

    async def get_notification_generator(self) -> None:
        """Returns the notification generator for sending boards across clients."""
        while True:
            message = yield
            msg = message["message"]
            room_name = message["room_name"]
            await self._notify(msg, room_name)

    def get_members(self, room_name: str) -> t.Optional[dict]:
        """Return all the members for a game_id i.e. room_name."""
        try:
            return self.connections[room_name]
        except Exception:
            return None

    async def push(self, msg: str, room_name: str = None) -> None:
        """Ascend notification data contaiing the message and room_name."""
        message_body = {"message": msg, "room_name": room_name}
        await self.generator.asend(message_body)

    async def connect(
        self,
        websocket: WebSocket,
        room_name: str,
        user_id: int,
        db: t.Optional[Session] = next(get_db()),
    ) -> t.Optional[str]:
        """Connet a websocket connection and register/update it in the DB."""
        game_obj = game.get_by_game_id(db, game_id=int(room_name))
        room_existed = False
        if game_obj:
            room_existed = True
            crud_response = game.set_player_two(
                db, game_id=int(room_name), player_id=user_id
            )
            if isinstance(crud_response, str):
                return crud_response
        else:
            return None

        await websocket.accept()

        if self.connections[room_name] == {} or len(self.connections[room_name]) == 0:
            self.connections[room_name] = {}
        self.connections[room_name].update({user_id: websocket})

        if room_existed:
            await notifier._notify(f"User#{user_id} has joined the game.", room_name)

        log.info(f"CONNECTIONS : {self.connections[room_name]}")

    def remove(
        self,
        _: WebSocket,
        room_name: str,
        user_id: int,
        db: t.Optional[Session] = next(get_db()),
    ) -> None:
        """Remove a websocket connection and close the chess game and mark the winner."""
        self.connections[room_name].pop(user_id)

        if self.connections[room_name]:
            remaing_user = next(iter(self.connections[room_name].keys()))
            game.mark_game_winner(db, game_id=int(room_name), winner_id=remaing_user)
        else:
            del self.connections[room_name]
            game.remove(db, id=int(room_name))

        log.info(
            f"CONNECTION REMOVED\nREMAINING CONNECTIONS : {self.connections[room_name]}"
        )

    async def _notify(self, message: str, room_name: str) -> None:
        """Notify all the members of the connection."""
        for _, websocket in self.connections[room_name].items():
            await websocket.send_text(message)


notifier = ChessNotifier()


@router.websocket("/{game_id}")
async def game_talking_endpoint(websocket: WebSocket, game_id: str) -> None:
    """Websocket endpoint for users in `game_id` to talk/send boards to each other."""
    user_id = await auth.JWTBearer().get_user_by_token_websocket(websocket)

    # The room name would be the game ID
    response = await notifier.connect(websocket, game_id, user_id)
    if isinstance(response, str):
        raise HTTPException(400, response)

    try:
        while True:
            data = await websocket.receive_text()

            room_members = (
                notifier.get_members(game_id)
                if notifier.get_members(game_id) is not None
                else {}
            )
            if websocket not in room_members.values():
                log.info("SENDER NOT IN ROOM MEMBERS: RECONNECTING")
                await notifier.connect(websocket, game_id, user_id)

            await notifier._notify(f"{data}", game_id)
    except WebSocketDisconnect:
        notifier.remove(websocket, game_id, user_id)
