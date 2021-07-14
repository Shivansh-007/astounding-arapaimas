from typing import Optional

from blessed import Terminal, formatters


class ThemeValidator:
    """Validates the theme config variable."""

    def __init__(self, theme: dict, term: Terminal) -> None:
        self.config = theme
        self.current_type = type(theme)
        self.target_type = type({"type": "dict"})
        self.term = term
        self.name = "theme"

    def validate_theme(self) -> bool:
        """Validates theme."""
        if not self.validate_type():
            return False

        required_keys = ("text", "board_edges", "white_squares", "black_squares")
        for key in required_keys:
            if key not in self.config.keys():
                print(
                    self.term.red_on_black(
                        f"Token {key} not found in loaded theme configuration."
                    )
                )
                return False

        for kind in self.config.values():
            theme = getattr(self.term, kind)
            if kind == "normal":
                # is not of type formatters.FormattingString
                continue

            if not isinstance(theme, formatters.FormattingString):
                print(f"Theme {kind!r} does not exist.")
                return False

        return True

    def fix_theme(self) -> Optional[str]:
        """Fixes the theme configuration variables."""
        if self.validate_theme():
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
