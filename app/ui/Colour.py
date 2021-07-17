"""
Contains all supported colour schemes.

# TODO: pass list of available schemes to some scheme picker.
# TODO: Figure out schemes and how to set and parse variables...?
"""
from blessed import Terminal


class ThemeError(Exception):
    """Error raised when invalid theme is requested."""

    def __init__(self, theme: str):
        self.theme = theme
        super().__init__(self.theme)


class ColourScheme:
    """Class implementing color scheme management."""

    # text = white_on_black
    themes = {
        "default": {
            "background": "white_on_black",
            "text": "normal",
            "board_edges": "normal",
            "white_squares": "snow",
            "black_squares": "gray69",
            "selected_square": "red",
            "legal_squares": "orange",
            "check": "yellow",
            "game_message": "black_on_blue",
            "ws_bottom": "green_on_black",
            "ws_top": "red_on_black",
            "ws_side_chars": "grey30_on_black",
            "ws_message": "blink_white_on_black",
            "ws_think": "grey10_bold_on_black",
            "gm_options": "bold_green",
            "gm_options_highlight": "black_on_green",
            "gm_exit": "bold_red",
            "gm_exit_highlight": "bold_white_on_red",
            "gm_option_message": "green",
            "gm_message": "white",
        },
        "mean_green": {
            "text": "green_on_black",
            "board_edges": "green_on_black",
            "white_squares": "black_on_green3",
            "black_squares": "green3_on_black",
            "selected_square": "on_red",
            "legal_squares": "on_orange",
            "game_message": "black_on_blue",
            "ws_bottom": "green3_on_black",
            "ws_top": "red_on_black",
            "ws_side_chars": "grey30_on_black",
            "ws_message": "blink_white_on_black",
            "ws_think": "grey10_bold_on_black",
            "gm_options": "bold_white_on_green",
            "gm_options_highlight": "black_on_green",
            "gm_exit": "bold_white_on_red",
            "gm_exit_highlight": "bold_white_on_red",
            "gm_option_message": "green",
            "gm_message": "white",
        },
    }

    def __init__(self, terminal: Terminal, theme: str = "default"):
        if theme in self.themes:
            theme = self.themes[theme]
            for element, style in theme.items():
                setattr(self, element, getattr(terminal, style))
            self.normal = terminal.normal
        else:
            raise ThemeError(f"'{theme}' is not a valid theme...")

    def return_themes(self) -> list:
        """Return the names of available themes."""
        return list(self.themes.keys())


if __name__ == "__main__":

    term = Terminal()
    theme_1 = ColourScheme(term, theme="default")
    theme_2 = ColourScheme(term, theme="mean_green")

    print(f"1: {theme_1.text}This is example text.{theme_1.normal}")
    print(
        f"2: {theme_2.text}This is another example with a different theme.{theme_2.normal}"
    )

    # assert type(ColourScheme(term, theme="error")) == type(Exception)
    # Leads to unhandled exception :| #REMOVE
