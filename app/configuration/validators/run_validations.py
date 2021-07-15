from typing import Union

from blessed import Terminal

from app.configuration.validators.theme_validator import ThemeValidator
from app.configuration.validators.token_validator import TokenValidator
from app.constants import Configuration


def fix_config(config: dict, term: Terminal) -> Union[dict, bool]:
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
        config["theme"] = Configuration.default_theme

    return config
