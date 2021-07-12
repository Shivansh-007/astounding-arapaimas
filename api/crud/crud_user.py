from typing import Optional

from sqlalchemy.orm import Session

from api.crud.base import CRUDBase
from api.models import User
from api.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """View providing CRUD operations on authenticated users."""

    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[User]:
        """Get a user model object by email."""
        return db.query(User).filter(User.user_id == user_id).first()

    def user_is_banned(self, db: Session, *, user_id: int) -> bool:
        """Returns whether the given user is banned or not."""
        user = self.get_by_user_id(db, user_id=user_id)
        if not user:
            return False

        return user.is_banned

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Make a new user object, and add it to the database."""
        db_obj = User(
            user_id=obj_in.user_id,
            username=obj_in.username,
            token_salt=obj_in.token_salt,
            is_staff=obj_in.is_staff,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_user_salt(
        self, db: Session, *, user_id: int, token_salt: str
    ) -> Optional[User]:
        """Updates a user's token salt with the new one."""
        user_obj = self.get_by_user_id(db, user_id=user_id)

        if not user_obj:
            return None

        user_obj.token_salt = token_salt

        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)
        return user_obj


user = CRUDUser(User)
