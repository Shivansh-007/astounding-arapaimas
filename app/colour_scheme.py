from blessed import Terminal


class ColourScheme:
    """Class implementing color scheme management."""

    def __init__(self, terminal: Terminal, theme: dict):
        self.theme = theme.copy()
        for element, style in self.theme.items():
            setattr(self, element, getattr(terminal, style))
        self.normal = terminal.normal

    def return_themes(self) -> list:
        """Return the names of available themes."""
        return list(self.theme.keys())
