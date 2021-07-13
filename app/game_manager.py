import sys

import ascii_art
from blessed import Terminal

term = Terminal()


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
            for i, option in enumerate(options):
                if i == curr_highlight and i != 3:
                    print(
                        term.move_x(term_positions[i])
                        + term.underline_bold_white_on_green
                        + str(option)
                        + term.normal
                        + term.move_x(0),
                        end="",
                    )
                elif i == curr_highlight and i == 3:
                    print(
                        term.move_x(term_positions[i])
                        + term.underline_bold_white_on_red
                        + str(option)
                        + term.normal
                        + term.move_x(0),
                        end="",
                    )
                elif i == 3:
                    print(
                        term.move_x(term_positions[i])
                        + term.bold_red
                        + str(option)
                        + term.normal
                        + term.move_x(0),
                        end="",
                    )
                else:
                    print(
                        term.move_x(term_positions[i])
                        + term.bold_green
                        + str(option)
                        + term.move_x(0),
                        end="",
                    )
                sys.stdout.flush()
            if curr_highlight != 9:
                print(
                    term.move_down(3)
                    + term.green
                    + term.center(brief[curr_highlight])
                    + term.move_x(0)
                    + "\n\n"
                    + term.white
                    + term.center("Press [ENTER] to confirm")
                    + term.move_up(5),
                    end="",
                )
            else:
                print(
                    term.move_down(3)
                    + term.white
                    + term.center("Press [TAB] for option selection")
                    + term.normal
                    + term.move_up(4)
                    + term.move_x(0)
                )

        def select_option() -> None:
            global curr_highlight
            if curr_highlight < 3:
                curr_highlight += 1
            else:
                curr_highlight = 0

        def next() -> None:
            if not curr_highlight:
                print(
                    "Created a new game"
                )  # Executes something when 'Create Game' is called
            elif curr_highlight == 1:
                pass  # Link to the actual game when selected
            elif curr_highlight == 2:
                print("Settings Selected")  # Link to settings file to access settings
            else:
                print("Exited the game")

        w, h = term.width, term.height
        options = [" Create Game ", " Join Game ", " Settings ", " Exit "]
        brief = [
            "Creates an new game and waits for an opponent to join",
            "Join a pre-existing game of your choice",
            "Change your game settings",
            "Exit the game",
        ]
        global curr_highlight
        curr_highlight = 9
        term_positions = [int(w * 0.38), int(w * 0.46), int(w * 0.54), int(w * 0.62)]

        title_split = ascii_art.TITLE.split("\n")
        with term.fullscreen(), term.cbreak():
            print(term.home + term.clear + term.move_y(int(h * 0.20)))
            for component in title_split:
                print(term.center(component))
            print(term.home + term.move_y(int(h * 0.60)))
            print_options()
            pressed = ""
            while pressed != "KEY_ENTER":
                pressed = term.inkey().name
                if pressed == "KEY_TAB":
                    select_option()
                    print_options()
        print(term.home + term.clear)
        next()

    def draw_tile(
        self,
        x: int = 0,
        y: int = 0,
        text: str = None,
        fg: str = "black",
        bg: str = "white",
    ) -> None:
        """Draws one tile and text inside of it."""
        style = getattr(self.term, f"{fg}_on_{bg}")
        for j in range(y, y + self.tile_height):
            for i in range(x, x + self.tile_width):
                with self.term.location(i, j):
                    print(style(" "))
        with self.term.location(x, y + (self.tile_height // 2)):
            print(style(str.center(text, self.tile_width)))

    def show_game_screen(self) -> None:
        """Shows the chess board."""
        pass

    def start_game(self) -> None:
        """Starts the chess game."""
        pass


game = Game()
game.show_game_menu()
