import sqlalchemy
from pydantic import validator

from api.db.base_class import Base


class Game(Base):
    """A game as used by the API."""

    game_id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True, unique=True)
    is_ongoing = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    winner_id = sqlalchemy.Column(sqlalchemy.BigInteger)
    player_one_id = sqlalchemy.Column(sqlalchemy.BigInteger)
    player_two_id = sqlalchemy.Column(sqlalchemy.BigInteger)

    @validator("player_one_id")
    def player_one_id_must_be_snowflake(cls, player_one_id: int) -> int:  # noqa: N805
        """Ensure the player_one_id is a valid discord snowflake."""
        if player_one_id.bit_length() <= 63:
            return player_one_id
        else:
            raise ValueError("player_one_id must fit within a 64 bit int.")
