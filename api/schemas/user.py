from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    """A schema representing a User model."""

    user_id: int
    username: str
    token_salt: Optional[str] = ""
    is_staff: Optional[bool] = False
    is_banned: Optional[bool] = False


class UserCreate(UserBase):
    """A schema representing a properties to received on User creation."""

    user_id: int
    username: str
    token_salt: str
    is_banned: bool


class UserUpdate(UserBase):
    """A schema representing a properties to received on User updatation."""

    user_id: int
    username: str
    token_salt: str
    is_staff: bool
    is_banned: bool


class UserInDBBase(UserBase):
    """A schema representing a properties shared by models stored in DB."""

    user_id: int

    class Config:  # noqa: D106
        orm_mode = True


class User(UserInDBBase):
    """A schema representing additional properties to return via API."""

    user_id: int
    username: str
    token_salt: str
    is_staff: bool
    is_banned: bool
