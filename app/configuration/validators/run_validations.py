from blessed import Terminal

from app.configuration.validators.theme_validator import ThemeValidator
from app.configuration.validators.token_validator import TokenValidator


def fix_config(config: dict, term: Terminal) -> bool:
    """Validates and fixes a configuration dictionary temporarily."""
    # Required Validations
    token = TokenValidator(config["token"], term).fix_token()
    if not token:
        return False
    config["token"] = token

    # Optional Validations
    if config.get("theme"):
        theme = ThemeValidator(config["theme"], term).fix_theme()
        if not theme:
            return False
        config["theme"] = theme
    else:
        print(term.blue_on_black("Loading default theme configuration..."))
        config["theme"] = {
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
    return True
