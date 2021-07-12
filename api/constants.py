import enum
from urllib.parse import unquote

import tomlkit
from decouple import config
from fastapi.templating import Jinja2Templates


class Connections:
    """How to connect to other, internal services."""

    DATABASE_URL = config("DATABASE_URL")


class Discord:
    """Any config required for interaction with Discord."""

    CLIENT_ID = config("CLIENT_ID")
    CLIENT_SECRET = config("CLIENT_SECRET")
    # starlette already quotes urls, so the url copied from discord ends up double encoded
    AUTH_URL = config("AUTH_URL", cast=unquote)
    TOKEN_URL = config("TOKEN_URL", default="https://discord.com/api/oauth2/token")
    USER_URL = config("USER_URL", default="https://discord.com/api/users/@me")
    WEBHOOK_URL = config("WEBHOOK_URL")
    API_BASE = "https://discord.com/api/v8"


class Server:
    """General config for the pixels server."""

    def _get_project_version() -> str:
        with open("pyproject.toml") as pyproject:
            file_contents = pyproject.read()

        return tomlkit.parse(file_contents)["tool"]["poetry"]["version"]

    VERSION = _get_project_version()
    JWT_SECRET = config("JWT_SECRET")

    LOG_LEVEL = config("LOG_LEVEL", default="INFO")
    BASE_URL = config("BASE_URL", default="http://127.0.0.1:8000")
    TEMPLATES = Jinja2Templates(directory="api/templates")


class AuthState(enum.Enum):
    """Represents possible outcomes of a user attempting to authorize."""

    NO_TOKEN = (
        "There is no token provided, provide one in an Authorization header in the format"
        " 'Bearer {your token here}' or navigate to /authorize to get one"
    )
    BAD_HEADER = "The Authorization header does not specify the Bearer scheme."
    INVALID_TOKEN = (
        "The token provided is not a valid token or has expired, navigate to "
        "/authorize to get a new one."
    )
    BANNED = "You are banned."
