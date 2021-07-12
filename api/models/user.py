from pydantic import validator
from sqlalchemy import BigInteger, Boolean, Column, String

from api.db.base_class import Base


class User(Base):
    """A user as used by the API."""

    user_id = Column(BigInteger, primary_key=True, unique=True)
    token_salt = Column(String, default="")
    is_staff = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)

    @validator("user_id")
    def user_id_must_be_snowflake(cls, user_id: int) -> int:  # noqa: N805
        """Ensure the user_id is a valid discord snowflake."""
        if user_id.bit_length() <= 63:
            return user_id
        else:
            raise ValueError("user_id must fit within a 64 bit int.")
