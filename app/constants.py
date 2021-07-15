import os

from app import ascii_art

GAME_WELCOME_BOTTOM = (
    ascii_art.PAWN,
    ascii_art.ROOK,
    ascii_art.KNIGHT,
    ascii_art.BISHOP,
    ascii_art.QUEEN,
    ascii_art.KING,
    ascii_art.BISHOP,
    ascii_art.KNIGHT,
    ascii_art.ROOK,
    ascii_art.PAWN,
)
GAME_WELCOME_TOP = (
    ascii_art.PAWN_I,
    ascii_art.ROOK_I,
    ascii_art.KNIGHT_I,
    ascii_art.BISHOP_I,
    ascii_art.QUEEN_I,
    ascii_art.KING_I,
    ascii_art.BISHOP_I,
    ascii_art.KNIGHT_I,
    ascii_art.ROOK_I,
    ascii_art.PAWN_I,
)

MENU_MAPPING = {
    " Create Game ": (
        "Creates an new game and waits for an opponent to join",
        "gm_options",
        "gm_options_highlight",
    ),
    " Join Game ": (
        "Join a pre-existing game of your choice",
        "gm_options",
        "gm_options_highlight",
    ),
    " Settings ": ("Change game settings", "gm_options", "gm_options_highlight"),
    " Exit ": ("Exit the game", "gm_exit", "gm_exit_highlight"),
}


class Configuration:
    """Configuration constants for the app."""

    configuration_paths = {
        "Windows": (
            os.path.expandvars("%APPDATA%/stealth-chess/config.yaml"),
            os.path.expandvars("%APPDATA%/stealth-chess/config.yml"),
        ),
        "Darwin": (
            os.path.expandvars("$HOME/.config/stealth-chess/config.yaml"),
            os.path.expandvars("$HOME/.config/stealth-chess/config.yml"),
        ),
        "Linux": (
            os.path.expandvars("$HOME/.config/stealth-chess/config.yaml"),
            os.path.expandvars("$HOME/.config/stealth-chess/config.yml"),
        ),
    }

    default_theme = {
        "background": "white_on_black",
        "text": "normal",
        "board_edges": "normal",
        "white_squares": "black_on_white",
        "black_squares": "normal",
        "game_message": "black_on_blue",
        "ws_bottom": "green_on_black",
        "ws_top": "red_on_black",
        "ws_side_chars": "grey30_on_black",
        "ws_message": "blink_white_on_black",
        "ws_think": "grey10_bold_on_black",
        "gm_options": "bold_green",
        "gm_options_highlight": "bold_white_on_green",
        "gm_exit": "bold_red",
        "gm_exit_highlight": "bold_white_on_red",
        "gm_option_message": "green",
        "gm_message": "white",
    }
