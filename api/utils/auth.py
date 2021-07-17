import logging
import secrets
import typing as t

from fastapi import HTTPException, Request, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN

from api.constants import AuthState, Server
from api.crud import user
from api.endpoints import get_db
from api.schemas.user import UserCreate

log = logging.getLogger(__name__)


class JWTBearer(HTTPBearer):
    """Dependency for routes to enforce JWT auth."""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        """Check if the supplied credentials are valid for this endpoint."""
        db = next(get_db())
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        credentials = credentials.credentials
        if not credentials:
            raise HTTPException(status_code=403, detail=AuthState.NO_TOKEN)

        try:
            token_data = jwt.decode(credentials, Server.JWT_SECRET)
        except JWTError:
            raise HTTPException(status_code=403, detail=AuthState.INVALID_TOKEN.value)

        user_id, token_salt = token_data["id"], token_data["salt"]
        user_state = user.get_by_user_id(db, user_id=user_id)

        # Handle bad scenarios
        if user_state is None or user_state.token_salt != token_salt:
            raise HTTPException(status_code=403, detail=AuthState.INVALID_TOKEN.value)
        elif user_state.is_banned:
            raise HTTPException(status_code=403, detail=AuthState.BANNED.value)

        request.state.user_id = int(user_id)
        return credentials

    async def get_user_by_token(self, request: Request) -> int:
        """Get user ID by authorization token."""
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        credentials = credentials.credentials

        token_data = jwt.decode(credentials, Server.JWT_SECRET)
        user_id, _ = token_data["id"], token_data["salt"]
        return int(user_id)

    async def get_user_by_plain_token(self, token: str) -> int:
        """Get user ID by plain authorization token passed as a string."""
        db = next(get_db())
        try:
            token_data = jwt.decode(token, Server.JWT_SECRET)
        except JWTError:
            raise HTTPException(status_code=403, detail=AuthState.INVALID_TOKEN.value)

        user_id, token_salt = token_data["id"], token_data["salt"]
        user_state = user.get_by_user_id(db, user_id=user_id)

        # Handle bad scenarios
        if user_state is None or user_state.token_salt != token_salt:
            raise HTTPException(status_code=403, detail=AuthState.INVALID_TOKEN.value)
        elif user_state.is_banned:
            raise HTTPException(status_code=403, detail=AuthState.BANNED.value)

        return int(user_id)

    async def get_user_by_token_websocket(
        self, websocket: WebSocket
    ) -> t.Optional[int]:
        """Get user ID by authorization token in the websocket header."""
        authorization = websocket.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None
        credentials = HTTPAuthorizationCredentials(
            scheme=scheme, credentials=credentials
        ).credentials

        token_data = jwt.decode(credentials, Server.JWT_SECRET)
        user_id, _ = token_data["id"], token_data["salt"]
        return int(user_id)


async def reset_user_token(
    user_id: str, username: str, db: t.Optional[Session] = next(get_db())
) -> str:
    """
    Ensure a user exists and create a new token for them.

    If the user already exists, their token is regenerated and the old is invalidated.
    """
    # Returns None if the user doesn't exist and false if they aren't banned
    is_banned = user.user_is_banned(db, user_id=int(user_id))
    if is_banned:
        raise PermissionError
    # 22 character long string
    token_salt = secrets.token_urlsafe(16)

    user_obj = user.update_user_salt(db, user_id=int(user_id), token_salt=token_salt)
    if not user_obj:
        user.create(
            db,
            obj_in=UserCreate(
                user_id=int(user_id),
                username=username,
                token_salt=token_salt,
                is_banned=False,
            ),
        )

    return jwt.encode(
        {"id": user_id, "salt": token_salt}, Server.JWT_SECRET, algorithm="HS256"
    )
