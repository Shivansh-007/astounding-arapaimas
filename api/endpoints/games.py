import logging
from collections import defaultdict
from datetime import datetime
from typing import Optional

import Chessnut.game
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket
from starlette.websockets import WebSocketDisconnect

from api import schemas
from api.crud import game
from api.endpoints import get_db
from api.utils import auth
from api.utils.chess import ChessBoard

log = logging.getLogger(__name__)
router = APIRouter(tags=["Game Endpoints"], dependencies=[Depends(auth.JWTBearer())])

INITIAL_GAME = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
BOARD_PREFIX = "BOARD"
INFO_PREFIX = "INFO"


@router.get("/new")
async def new_game_create(request: Request) -> dict:
    """
    Make a new chess game and send link to game room.

    A user can only make a room if they don't have one existing already,
    so it first verifies if the user is in a game or not and then creates
    one for them.

    ### Example python script
    ```py
    import httpx

    token = input("TOKEN: ")
    headers = {"Authorization": f"Bearer {token}"}

    r = httpx.put("http://127.0.0.1:8000/game/new", headers=headers)
    game_endpoint = r.json()["room"]

    print(game_endpoint)
    # /game/1626296948
    ```
    """
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

    return {"room": f"{game_id}"}


class ChessNotifier:
    """Manages chess room sessions and members."""

    def __init__(self):
        self.connections: dict = defaultdict(dict)
        self.generator = self.get_notification_generator()
        self.chess_boards: dict = dict()

        self.db = next(get_db())

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
        self, websocket: WebSocket, room_name: str, user_id: int
    ) -> Optional[str]:
        """Connet a websocket connection and register/update it in the DB."""
        # Player 2 returns a string in case of invalid game ID (game doesn't exist)
        # or if the player 2 is already assigned and game has began!
        game_obj = game.get_by_game_id(self.db, game_id=int(room_name))

        if not game_obj:
            return "Invalid Game ID, make a game with /game/new and then connect here."
        if len(self.connections[room_name]) == 1:  # one user in room
            player_count = game.get_player_count(
                self.db, game_id=int(room_name)
            )  # get how many in db
            if player_count == 1:  # only one in db
                if game.player_already_in_game(self.db, user_id=user_id):
                    return "You are already in a game."
                crud_response = game.set_player_two(
                    self.db, game_id=int(room_name), player_id=user_id
                )
                if isinstance(crud_response, str):
                    return crud_response

            elif (
                player_count == 2
                and user_id not in self.connections[room_name].keys()
                and user_id in [game_obj.player_one_id, game_obj.player_two_id]
            ):  # coming after disconnect
                self.connections[room_name].update({user_id: websocket})
            else:
                return "only 2 player per game lobby allowed"

        await websocket.accept()

        if self.connections[room_name] == {} or len(self.connections[room_name]) == 0:
            self.connections[room_name] = {}
        self.connections[room_name].update({user_id: websocket})

        await notifier._notify(
            f"{INFO_PREFIX}::JOIN::User#{user_id} has joined the game.", room_name
        )
        log.info(f"CONNECTIONS : {self.connections[room_name]}")

        # notify players after updating connections dict

        if room_name not in self.chess_boards.keys():  # first connection
            if len(self.connections[room_name]) == 1:  # only one player has joined
                if game_obj.player_one_id == user_id:
                    await self._notify_private(
                        websocket, f"{INFO_PREFIX}::PLAYER::p1", room_name
                    )
            elif game_obj.player_two_id == user_id:
                await self._notify_private(
                    websocket, f"{INFO_PREFIX}::PLAYER::p2", room_name
                )
                log.debug(f"setting new board for {room_name}")
                self.chess_boards.update(
                    {f"{room_name}": ChessBoard(INITIAL_GAME, int(room_name))}
                )  # make a new board for a room
                await self._notify(f"{INFO_PREFIX}::READY", room_name)
        else:
            # coming here after disconnect
            # tell if player 1 or player 2
            if game_obj.player_one_id == user_id:
                await self._notify_private(
                    websocket, f"{INFO_PREFIX}::PLAYER::p1", room_name
                )
            elif game_obj.player_two_id == user_id:
                await self._notify_private(
                    websocket, f"{INFO_PREFIX}::PLAYER::p2", room_name
                )

            await self._notify_private(websocket, f"{INFO_PREFIX}::READY", room_name)
            await self._notify_private(
                websocket,
                f"{BOARD_PREFIX}::{BOARD_PREFIX}::{self.chess_boards[room_name].give_board()}",
                room_name,
            )
            log.debug(f"{room_name} not empty, don't init board")

    def remove(self, _: WebSocket, room_name: str, user_id: int) -> None:
        """Remove a websocket connection and close the chess game and mark the winner."""
        self.connections[room_name].pop(user_id)

        if self.connections[room_name]:
            remaing_user = next(iter(self.connections[room_name].keys()))
            game.mark_game_winner(
                self.db, game_id=int(room_name), winner_id=remaing_user
            )
        else:
            del self.connections[room_name]
            del self.chess_boards[room_name]
            game.remove(self.db, id=int(room_name))

        log.info(
            f"CONNECTION REMOVED\nREMAINING CONNECTIONS : {self.connections[room_name]}"
        )

    async def _notify(self, message: str, room_name: str) -> None:
        """Notify all the members of the connection."""
        for _, websocket in self.connections[room_name].items():
            await websocket.send_text(message)

    async def _notify_private(
        self, web_socket: WebSocket, message: str, room_name: str
    ) -> None:
        """Notify only one user."""
        if web_socket in self.connections[room_name].values():
            await web_socket.send_text(message)

    async def mark_game_over(self, _: WebSocket, user: str, game_id: int) -> None:
        """Mark the `user` as the game winner and send game over message."""
        game_obj = game.get_by_game_id(self.db, game_id=game_id)
        game.mark_game_winner(
            self.db,
            game_id=game_id,
            winner_id=game_obj.player_one_id
            if user == "p1"
            else game_obj.player_two_id,
        )
        for _, websocket in self.connections[str(game_id)].items():
            await websocket.send_text(f"{BOARD_PREFIX}::OVER::{user}")

        room_name = str(game_id)
        del self.connections[room_name]
        del self.chess_boards[room_name]


notifier = ChessNotifier()


@router.websocket("/{game_id}")
async def game_talking_endpoint(websocket: WebSocket, game_id: str) -> None:
    """
    Websocket endpoint for users in `game_id` to talk/send boards to each other.

    All the communication in two games is done and here, the player moves, player joins,
    reseting the game, player chat, etc.

    ### Example python code
    ```py
    import websocket

    token = input("TOKEN: ")
    headers = {"Authorization": f"Bearer {token}"}
    game_id = 1626474066  # Example

    ws_local = websocket.WebSocket()
    ws_local.connect(f"ws://127.0.0.1:800/game/{game_id}")

    try:
        while True:
            data_received = ws_local.recv()
            ...
    except Exception as error:
        print(error)
        ws_local.close(reason=fb"Program terminated with error: {error}")
        raise
    ```
    """
    user_id: int = await auth.JWTBearer().get_user_by_token_websocket(websocket)

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
                            notifier.chess_boards[game_id].move_piece(value)
                        await notifier._notify(
                            f"{BOARD_PREFIX}::{BOARD_PREFIX}::{notifier.chess_boards[game_id].give_board()}",
                            game_id,
                        )  # send new FEN representation if move is valid
                    elif command == "GET_ALL_MOVES":
                        await notifier._notify(
                            f"{BOARD_PREFIX}::{notifier.chess_boards[game_id].all_available_moves()}",
                            game_id,
                        )  # send all moves available for the current active player
                    elif command == "GET_BOARD":
                        await notifier._notify_private(
                            websocket,
                            f"{BOARD_PREFIX}::{BOARD_PREFIX}::{notifier.chess_boards[game_id].give_board()}",
                            game_id,
                        )
                    elif command == "RESET":
                        notifier.chess_boards[game_id].reset()
                        await notifier._notify(
                            f"{BOARD_PREFIX}::{BOARD_PREFIX}::{notifier.chess_boards[game_id].give_board()}",
                            game_id,
                        )  # reset board and send new FEN
                    elif command == "SURRENDER":
                        # value is the user who surrendered, e.g. SURRENDER::p1 i.e. p1 surrendered the game
                        await notifier.mark_game_over(
                            websocket, ("p2", "p1")[value == "p2"], int(game_id)
                        )
                    elif command == "WINNER":
                        # value is the user who won the game e.g. WINNER::p2 i.e. p2 won the chess game
                        await notifier.mark_game_over(websocket, value, int(game_id))
                    else:
                        log.debug(f"invalid command {command,value}")
                except Chessnut.game.InvalidMove:
                    log.debug(f"invalid move {value} , game_id : {game_id}")
                    pass

            if websocket not in room_members.values():
                log.info("SENDER NOT IN ROOM MEMBERS: RECONNECTING")
                await notifier._notify("INFO::DISCONNECT", game_id)
                await notifier.connect(websocket, game_id, user_id)

    except WebSocketDisconnect:
        notifier.remove(websocket, game_id, user_id)
