class Game:
    """Main class of the project."""

    """
    That will handle :-
    the menus
    connection with the server
    printing of the chessboard
    turns of players when playing locally
    """

    def __init__(self):
        self.players = None
        self.game_id = None  # the game lobby id that the server will provide for online multiplayer
        self.server_ip = None
        self.chess_board = None

    def create_lobby(self) -> int:
        """Used to create a game lobby on the server or locally."""
        pass

    def show_welcome_screen(self) -> None:
        """Prints startup screen."""
        pass

    def show_game_menu(self) -> None:
        """Prints the screen to choose to play online or offline."""
        pass

    def print_game_screen(self) -> None:
        """Prints the chess board."""
        """ that follows all rules of the game and the time taken for a turn"""
        pass

    def start_game(self) -> int:
        """Starts the chess game."""
        pass
