import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from api.crud import game
from api.endpoints import get_db
from api.schemas import game
from api.utils import auth

log = logging.getLogger(__name__)
router = APIRouter(tags=["Game Endpoints"], dependencies=[Depends(auth.JWTBearer())])


@router.get("/new", response_class=Response)
async def new_game(request: Request, db: Session = Depends(get_db)) -> Response:
    """Create a new game object and web socket thread for that game."""
    from api.main import socket_manager as sm

    user_id = await auth.JWTBearer().get_user_by_token(request)
    game_id = f"{str(user_id)}{str(datetime.now().timestamp)}"

    new_game_obj = game.GameCreate(
        game_id=game_id,
        is_ongoing=True,
        winner_id=None,
        player_one_id=user_id,
        player_two_id=None,
    )
    game.create(db, obj_in=new_game_obj)
    sm.enter_room(user_id, game_id)


@router.get("/join/{game_id}", response_class=Response)
async def join_game(
    request: Request, game_id: int, db: Session = Depends(get_db)
) -> Response:
    """Join the current user to the game with id `game_id` and its socket.io room."""
    from api.main import socket_manager as sm

    user_id = await auth.JWTBearer().get_user_by_token(request)
    response = game.set_player_two(db, game_id=game_id, user_id=user_id)
    if isinstance(response, str):
        return HTTPException(400, response)
    else:
        sm.enter_room(user_id, game_id)
