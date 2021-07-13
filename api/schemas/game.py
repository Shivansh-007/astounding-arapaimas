from typing import Optional

from pydantic import BaseModel


class GameBase(BaseModel):
    """A schema representing a Game model."""

    game_id: int
    is_ongoing: Optional[bool] = True
    winner_id: Optional[int] = 0
    player_one_id: int
    player_two_id: Optional[int] = 0


class GameCreate(GameBase):
    """A schema representing a properties to received on Game creation."""

    game_id: int
    is_ongoing: int
    winner_id: int
    player_one_id: int
    player_two_id: int


class GameUpdate(GameBase):
    """A schema representing a properties to received on Game updatation."""

    game_id: int
    is_ongoing: int
    winner_id: int
    player_one_id: int
    player_two_id: int


class GameInDBBase(GameBase):
    """A schema representing a properties shared by models stored in DB."""

    user_id: int

    class Config:  # noqa: D106
        orm_mode = True


class Game(GameInDBBase):
    """A schema representing additional properties to return via API."""

    game_id: int
    is_ongoing: int
    winner_id: int
    player_one_id: int
    player_two_id: int
