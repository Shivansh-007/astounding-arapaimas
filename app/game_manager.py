import ascii_art
from blessed import Terminal


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
        self.term = Terminal()

    def create_lobby(self) -> int:
        """Used to create a game lobby on the server or locally."""
        pass

    def show_welcome_screen(self) -> None:
        """Prints startup screen."""
        print(self.term.home + self.term.white_on_black + self.term.clear)
        # draw bottom chess pieces
        sequence = (
            ascii_art.PAWN,
            ascii_art.ROOK,
            ascii_art.KNIGHT,
            ascii_art.BISHOP,
            ascii_art.QUEEN,
            ascii_art.KING,
            ascii_art.BISHOP,
            ascii_art.KNIGHT,
            ascii_art.ROOK,
            ascii_art.PAWN,
        )
        padding = (
            self.term.width
            - sum(max(len(p) for p in piece.split("\n")) for piece in sequence)
        ) // 2
        position = 0
        for piece in sequence:
            for i, val in enumerate(piece.split("\n")):
                with self.term.location(
                    padding + position,
                    self.term.height - (len(piece.split("\n")) + 1) + i,
                ):
                    print(self.term.green_on_black(val))
            position += max(len(p) for p in piece.split("\n"))

        # draw top chess pieces
        sequence = (
            ascii_art.PAWN_I,
            ascii_art.ROOK_I,
            ascii_art.KNIGHT_I,
            ascii_art.BISHOP_I,
            ascii_art.QUEEN_I,
            ascii_art.KING_I,
            ascii_art.BISHOP_I,
            ascii_art.KNIGHT_I,
            ascii_art.ROOK_I,
            ascii_art.PAWN_I,
        )
        position = 0
        for piece in sequence:
            for i, val in enumerate(piece.split("\n")):
                with self.term.location(padding + position, 1 + i):
                    print(self.term.red_on_black(val))
            position += max(len(p) for p in piece.split("\n"))

        # draw side characters
        for i, char in enumerate(ascii_art.FEN[: self.term.height - 2]):
            with self.term.location(0, 1 + i):
                print(self.term.grey30_on_black(char))
            with self.term.location(self.term.width, 1 + i):
                print(self.term.grey30_on_black(char))

        # draw box center message
        message = "PRESS ANY KEY TO START"
        padding = (self.term.width - len(message)) // 2
        with self.term.location(padding, self.term.height // 2):
            print(self.term.blink_white_on_black(message))

        # draw THINK box
        padding = (self.term.width - len(ascii_art.THINK.split("\n")[0])) // 2
        for i, val in enumerate(ascii_art.THINK.split("\n")):
            with self.term.location(
                5, self.term.height - len(ascii_art.THINK.split("\n")) + i
            ):
                print(self.term.grey10_bold_on_black(val))

    def show_game_menu(self) -> None:
        """Prints the screen to choose to play online or offline."""
        pass

    def show_game_screen(self) -> None:
        """Shows the chess board."""
        pass

    def start_game(self) -> None:
        """Starts the chess game."""
        pass
