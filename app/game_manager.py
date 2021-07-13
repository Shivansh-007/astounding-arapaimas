import sys
from copy import deepcopy

import ascii_art
from blessed import Terminal

term = Terminal()

PIECES = "".join(chr(9812 + x) for x in range(12))
print(PIECES)
ROW = ("A", "B", "C", "D", "E", "F", "G", "H")
COL = tuple(map(str, range(1, 9)))

# rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
initial_game = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p"] * 8,
    ["em"] * 8,
    ["em"] * 8,
    ["em"] * 8,
    ["em"] * 8,
    ["P"] * 8,
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
]


mapper = {
    "em": ("", "white"),
    "k": (PIECES[0], "white"),
    "q": (PIECES[1], "white"),
    "r": (PIECES[2], "white"),
    "b": (PIECES[3], "white"),
    "n": (PIECES[4], "white"),
    "p": (PIECES[5], "white"),
    "K": (PIECES[6], "black"),
    "Q": (PIECES[7], "black"),
    "R": (PIECES[8], "black"),
    "B": (PIECES[9], "black"),
    "N": (PIECES[10], "black"),
    "P": (PIECES[11], "black"),
}


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
        self.term = Terminal()
        self.players = None
        self.game_id = None  # the game lobby id that the server will provide for online multiplayer
        self.server_ip = None
        self.chess_board = deepcopy(initial_game)
        self.tile_width = 6
        self.tile_height = 3
        self.offset_x = 0
        self.offset_y = 0
        self.x = 0
        self.y = 0
        # self.my_color = 'white' # for future
        self.white_move = True  # this will chnage in multiplayer game

    # TODO:: IS THIS NEEDED?
    def __len__(self) -> int:
        return 8

    def create_lobby(self) -> int:
        """Used to create a game lobby on the server or locally."""
        pass

    def show_welcome_screen(self) -> None:
        """Prints startup screen."""
        pass

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
        print(self.term.fullscreen())
        print(self.term.home + self.term.clear)
        for j in range(len(self)):
            # for every col we need to add number too!
            num = len(self) - j
            x = self.tile_width // 2
            y = j * self.tile_height + self.tile_height // 2
            with self.term.location(x, y):
                print(num)
            for i in range(len(self)):
                if (i + j) % 2 == 0:
                    bg = "blue"
                else:
                    bg = "green"
                piece, color = mapper[self.chess_board[j][i]]
                self.draw_tile(
                    x * 2 + i * (self.tile_width + self.offset_x),
                    j * (self.tile_height + self.offset_y),
                    text=piece,
                    fg=color,
                    bg=bg,
                )
        for i in range(len(self)):
            with self.term.location(
                x * 2 - 1 + i * self.tile_width, len(self) * self.tile_height
            ):
                print(str.center(ROW[i], len(self)))
        print(self.term.move_y(self.term.height - 4))

    def start_game(self) -> int:
        """Starts the chess game."""
        while True:
            self.show_game_screen()
            if self.white_move:
                print(
                    self.term.black_on_blue(
                        self.term.center("Which piece you want to play white?")
                    )
                )
            else:
                print(
                    self.term.black_on_blue(
                        self.term.center("Which piece you want to play black?")
                    )
                )
            # with self.term.cbreak():
            inp = input()
            # print(inp)
            # TODO:: VALIDATION
            row = ROW.index(inp[0].upper())
            col = len(self) - int(inp[1])
            # TODO:: VALIDATION
            if self.chess_board[row][col] != "em":
                inp2 = input()
                if inp == inp2:
                    print("LOL try again!")
                    continue
                # TODO:: VALIDATION
                row2 = ROW.index(inp2[0].upper())
                col2 = len(self) - int(inp2[1])
                print(row, col, row2, col2)
                piece = self.chess_board[row][col]
                self.chess_board[row][col] = "em"
                self.chess_board[row2][col2] = piece
                # TODO:: UPDATE VIEW
            else:
                print("Invalid move")
        return 1


game = Game()
game.show_game_menu()
