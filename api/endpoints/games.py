import logging
from collections import defaultdict
from datetime import datetime
from typing import Optional

import Chessnut.game
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from api import schemas
from api.crud import game
from api.endpoints import get_db
from api.utils import auth
from app.chess import ChessBoard

log = logging.getLogger(__name__)
router = APIRouter(tags=["Game Endpoints"], dependencies=[Depends(auth.JWTBearer())])

INITIAL_GAME = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
BOARD_PREFIX = "BOARD"  # add this to yaml config


@router.get("/new")
async def new_game_create(request: Request) -> dict:
    """Make a new chess game and send link to game room."""
    user_id = await auth.JWTBearer().get_user_by_token(request)
    db = next(get_db())

    if game.player_already_in_game(db, user_id=user_id):
        return {"message": "You are already in a game."}

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

    def get_members(self, room_name: str) -> Optional[dict]:
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
        db: Optional[Session] = next(get_db()),
    ) -> Optional[str]:
        """Connet a websocket connection and register/update it in the DB."""
        # Player 2 returns a string in case of invalid game ID (game doesn't exist)
        # or if the player 2 is already assigned and game has began!
        print(int(room_name))
        game_obj = game.get_by_game_id(db, game_id=int(room_name))

        if not game_obj:
            return "Invalid Game ID, make a game with /game/new and then connect here."

        if self.connections[room_name] != {}:
            # Player 1 is already set and is waiting for Player 2
            if game.player_already_in_game(db, user_id=user_id):
                return "You are already in a game."

            crud_response = game.set_player_two(
                db, game_id=int(room_name), player_id=user_id
            )
            if isinstance(crud_response, str):
                return crud_response
            # Notify the room that player 2 connected
            await self._notify("INFO::p2", room_name)
        else:
            await self._notify("INFO::p1", room_name)

        await websocket.accept()

        if self.connections[room_name] == {} or len(self.connections[room_name]) == 0:
            self.connections[room_name] = {}
        self.connections[room_name].update({user_id: websocket})

        await notifier._notify(f"User#{user_id} has joined the game.", room_name)
        log.info(f"CONNECTIONS : {self.connections[room_name]}")

    def remove(
        self,
        _: WebSocket,
        room_name: str,
        user_id: int,
        db: Optional[Session] = next(get_db()),
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
    user_id: int = await auth.JWTBearer().get_user_by_token_websocket(websocket)

    # The room name would be the game ID
    response = await notifier.connect(websocket, game_id, user_id)
    if isinstance(response, str):
        raise HTTPException(400, response)

    try:
        chess_board = ChessBoard(
            INITIAL_GAME
        )  # init a new game as soon as one player connects
        await notifier._notify(f"{BOARD_PREFIX}::{chess_board.give_board()}", game_id)

        while True:
            data = await websocket.receive_text()

            room_members = (
                notifier.get_members(game_id)
                if notifier.get_members(game_id) is not None
                else {}
            )
            # syntax PREFIX::COMMAND::<VALUE>
            prefix, command, value = "", "", ""
            try:
                data = data.split("::")
                prefix = data[0]
                command = data[1]
            except IndexError:
                log.debug(f"Invalid command {data}")
            if len(data) == 3:
                value = data[2]

            if prefix == BOARD_PREFIX:
                # all chess_board related stuff here
                try:
                    if command == "MOVE":
                        if value:
                            chess_board.move_piece(value)
                        await notifier._notify(
                            f"{BOARD_PREFIX}::{chess_board.give_board()}", game_id
                        )  # send new FEN representation if move is valid
                    elif command == "GET_ALL_MOVES":
                        await notifier._notify(
                            f"{BOARD_PREFIX}::{chess_board.all_available_moves()}",
                            game_id,
                        )  # send all moves available for the current active player
                    elif command == "RESET":
                        chess_board.reset()
                        await notifier._notify(
                            f"{BOARD_PREFIX}::{chess_board.give_board()}", game_id
                        )  # reset board and send new FEN
                    else:
                        log.debug(f"invalid command {command,value}")
                except Chessnut.game.InvalidMove:
                    log.debug(f"invalid move {value} , game_id : {game_id}")
                    pass

            if websocket not in room_members.values():
                log.info("SENDER NOT IN ROOM MEMBERS: RECONNECTING")
                await notifier.connect(websocket, game_id, user_id)

    except WebSocketDisconnect:
        notifier.remove(websocket, game_id, user_id)
