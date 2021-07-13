import sys

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
        self.curr_highlight = None

    def create_lobby(self) -> int:
        """Used to create a game lobby on the server or locally."""
        pass

    def show_welcome_screen(self) -> str:
        """Prints startup screen and return pressed key."""
        with self.term.cbreak(), self.term.hidden_cursor():
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
            keypress = self.term.inkey()
            return keypress

    def show_game_menu(self) -> None:
        """Prints the game-menu screen."""

        def print_options() -> None:
            for i, option in enumerate(options):  # updates the options
                if i == self.curr_highlight and i != 3:
                    print(
                        self.term.move_x(term_positions[i])
                        + self.term.underline_bold_white_on_green
                        + str(option)
                        + self.term.normal
                        + self.term.move_x(0),
                        end="",
                    )
                elif i == self.curr_highlight and i == 3:
                    print(
                        self.term.move_x(term_positions[i])
                        + self.term.underline_bold_white_on_red
                        + str(option)
                        + self.term.normal
                        + self.term.move_x(0),
                        end="",
                    )
                elif i == 3:
                    print(
                        self.term.move_x(term_positions[i])
                        + self.term.bold_red
                        + str(option)
                        + self.term.normal
                        + self.term.move_x(0),
                        end="",
                    )
                else:
                    print(
                        self.term.move_x(term_positions[i])
                        + self.term.bold_green
                        + str(option)
                        + self.term.move_x(0),
                        end="",
                    )
                sys.stdout.flush()
            if self.curr_highlight != 9:
                print(
                    self.term.move_down(3)
                    + self.term.green
                    + self.term.center(brief[self.curr_highlight])
                    + self.term.move_x(0)
                    + "\n\n"
                    + self.term.white
                    + self.term.center("Press [ENTER] to confirm")
                    + self.term.move_up(5),
                    end="",
                )
            else:
                print(
                    self.term.move_down(3)
                    + self.term.white
                    + self.term.center("Press [TAB] for option selection")
                    + self.term.normal
                    + self.term.move_up(4)
                    + self.term.move_x(0)
                )

        def select_option() -> None:  # updates the highlighter variable
            if self.curr_highlight < 3:
                self.curr_highlight += 1
            else:
                self.curr_highlight = 0

        def next() -> None:  # Executes the selected option
            if not self.curr_highlight:
                print(
                    "Created a new game"
                )  # Executes something when 'Create Game' is called
            elif self.curr_highlight == 1:
                pass  # Link to the actual game when selected
            elif self.curr_highlight == 2:
                print("Settings Selected")  # Link to settings file to access settings
            else:
                print("Exited the game")

        w, h = self.term.width, self.term.height
        options = [" Create Game ", " Join Game ", " Settings ", " Exit "]
        brief = [
            "Creates an new game and waits for an opponent to join",
            "Join a pre-existing game of your choice",
            "Change your game settings",
            "Exit the game",
        ]
        self.curr_highlight = 9
        term_positions = [int(w * 0.38), int(w * 0.46), int(w * 0.54), int(w * 0.62)]

        title_split = ascii_art.menu_logo.split("\n")
        max_chars = len(max(title_split, key=len))
        with self.term.fullscreen(), self.term.cbreak():
            print(self.term.home + self.term.clear + self.term.move_y(int(h * 0.10)))
            for component in title_split:  # Prints centered title
                component = str(component) + " " * (max_chars - len(component))
                print(self.term.center(component))
            print(
                self.term.home + self.term.move_y(int(h * 0.70))
            )  # Sets the cursor to the options position
            print_options()
            pressed = ""
            while pressed != "KEY_ENTER":  # Loops till the user chooses an option
                pressed = self.term.inkey().name
                if pressed == "KEY_TAB":
                    select_option()
                    print_options()
        print(self.term.home + self.term.clear)  # Resets the terminal
        next()

    def show_game_screen(self) -> None:
        """Shows the chess board."""
        pass

    def start_game(self) -> None:
        """Starts the chess game."""
        pass


game = Game()
game.show_game_menu()
