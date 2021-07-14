from typing import Optional

from blessed import Terminal

from app.configuration.validators.validator_base import Validator


class TokenValidator(Validator):
    """Validates the token config variable."""

    def __init__(self, token: str, term: Terminal) -> None:
        self.token = token
        self.term = term
        super().__init__(self.token, "string type", "token", term)

    def validate_token(self) -> bool:
        """Validates token."""
        if not self.validate_type():
            return False

        return True

    def fix_token(self) -> Optional[str]:
        """Fixes the prompt_start configuration variables."""
        if self.validate_token():
            return self.token
