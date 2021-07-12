class Player:
    """Class for defining a player."""

    def __init__(self, player_id: str):
        self.id = player_id
        self.game_history = None  # stores the result of the previous games


class Game:
    """
    Main class of the project.

    That will handle :-
       - the menus
       - connection with the server
       - printing of the chessboard
       - turns of players when playing locally
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

    def show_game_screen(self) -> None:
        """Shows the chess board."""
        pass

    def start_game(self) -> int:
        """Starts the chess game."""
        pass
