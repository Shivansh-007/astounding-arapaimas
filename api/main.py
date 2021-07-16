import logging

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.constants import Server
from api.endpoints import auth, games

log = logging.getLogger(__name__)

app = FastAPI(docs_url=None, redoc_url=None)

app.include_router(router=auth.router)
app.include_router(router=games.router, prefix="/game")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="api/static"), name="static")


@app.exception_handler(StarletteHTTPException)
async def my_exception_handler(
    request: Request, exception: StarletteHTTPException
) -> Response:
    """Custom exception handler to render template for 404 error."""
    if exception.status_code == 404:
        return Server.TEMPLATES.TemplateResponse(
            name="not_found.html",
            context={"request": request},
            status_code=exception.status_code,
        )
    return PlainTextResponse(str(exception.detail), status_code=exception.status_code)


@app.on_event("startup")
async def startup() -> None:
    """Setup logging and create asyncpg and redis connection pools on startup."""
    # Setup logging
    format_string = "[%(asctime)s] [%(process)d] [%(levelname)s] %(name)s - %(message)s"
    date_format_string = "%Y-%m-%d %H:%M:%S %z"
    logging.basicConfig(
        format=format_string,
        datefmt=date_format_string,
        level=getattr(logging, Server.LOG_LEVEL.upper()),
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    """Close down the app."""
    ...
