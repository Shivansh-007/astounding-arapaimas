from typing import Optional

from blessed import Terminal


class TokenValidator:
    """Validates the token config variable."""

    def __init__(self, token: str, term: Terminal) -> None:
        self.config = token
        self.current_type = type(token)
        self.target_type = type("string")
        self.term = term
        self.name = "token"

    def validate_token(self) -> bool:
        """Validates token."""
        if not self.validate_type():
            return False

        return True

    def fix_token(self) -> Optional[str]:
        """Fixes the prompt_start configuration variables."""
        if self.validate_token():
            return self.config

    def validate_type(self) -> bool:
        """Validates the type of a given configuration."""
        if self.current_type is not self.target_type:
            print(
                self.term.red_on_black(
                    f"Invalid {self.name} option type, use type {self.target_type.__name__}, "
                    f"not {self.current_type.__name__}."
                )
            )
            return False

        return True
