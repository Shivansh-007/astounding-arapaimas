from typing import Any

from blessed import Terminal


class Validator:
    """Base class for all other configuration validators that provides some basic checks."""

    def __init__(self, config: Any, type_eg: Any, name: str, term: Terminal) -> None:
        self.config = config
        self.current_type = type(config)
        self.target_type = type(type_eg)
        self.term = term
        self.name = name

    def validate_type(self) -> bool:
        """Validates the type of a given configuration."""
        if self.current_type is not self.target_type:
            print(
                self.term.red(
                    f"Invalid {self.name} option type, use type {self.target_type.__name__}, "
                    f"not {self.current_type.__name__}."
                )
            )
            return False

        return True
