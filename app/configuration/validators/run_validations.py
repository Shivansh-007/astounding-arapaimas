from typing import Optional

from blessed import Terminal

from app.configuration.validators.token_validator import TokenValidator


def fix_config(config: dict, term: Terminal) -> Optional[bool]:
    """Validates and fixes a configuration dictionary temporarily."""
    token = TokenValidator(config["token"], term).fix_token()
    if not token:
        return False
    config["token"] = token
