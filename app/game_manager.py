from copy import deepcopy

from blessed import Terminal

from app import ascii_art, constants
from app.chess import ChessBoard
from app.ui.Colour import ColourScheme


PIECES = "".join(chr(9812 + x) for x in range(12))
print(PIECES)
COL = ("A", "B", "C", "D", "E", "F", "G", "H")
ROW = tuple(map(str, range(1, 9)))

INITIAL_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
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

BLACK_PIECES = ("r", "n", "b", "q", "k", "p")

WHITE_PIECES = ("R", "N", "B", "Q", "K", "P")

mapper = {
    "em": ("", "white"),
    "K": (PIECES[0], "white"),
    "Q": (PIECES[1], "white"),
    "R": (PIECES[2], "white"),
    "B": (PIECES[3], "white"),
    "N": (PIECES[4], "white"),
    "P": (PIECES[5], "white"),
    "k": (PIECES[6], "black"),
    "q": (PIECES[7], "black"),
    "r": (PIECES[8], "black"),
    "b": (PIECES[9], "black"),
    "n": (PIECES[10], "black"),
    "p": (PIECES[11], "black"),
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
        self.colour_scheme = "default"
        self.theme = ColourScheme(self.term, theme=self.colour_scheme)
        # self.chess_board = deepcopy(initial_game)
        self.chess = ChessBoard(INITIAL_FEN)
        # print(ChessBoard(INITIAL_FEN))
        self.chess_board = self.fen_to_board(self.chess.give_board())
        self.fen = INITIAL_FEN
        self.tile_width = 6
        self.tile_height = 3
        self.offset_x = 0
        self.offset_y = 0
        self.x = 0
        self.y = 0
        # self.my_color = 'white' # for future
        self.white_move = True  # this will change in multiplayer game
        self.selected_row = 0
        self.selected_col = 0
        self.possible_moves = []
        # self.handle_arrows()

    # TODO:: IS THIS NEEDED?
    def __len__(self) -> int:
        return 8

    def create_lobby(self) -> int:
        """Used to create a game lobby on the server or locally."""
        pass

    def show_welcome_screen(self) -> str:
        """Prints startup screen and return pressed key."""
        with self.term.cbreak():
            print(self.term.home + self.theme.background + self.term.clear)
            # draw bottom chess pieces
            padding = (
                self.term.width
                - sum(
                    max(len(p) for p in piece.split("\n"))
                    for piece in constants.GAME_WELCOME_TOP
                )
            ) // 2
            position = 0
            for piece in constants.GAME_WELCOME_TOP:
                for i, val in enumerate(piece.split("\n")):
                    with self.term.location(
                        padding + position,
                        self.term.height - (len(piece.split("\n")) + 1) + i,
                    ):
                        print(self.theme.ws_bottom(val))
                position += max(len(p) for p in piece.split("\n"))

            # draw top chess pieces
            position = 0
            for piece in constants.GAME_WELCOME_BOTTOM:
                for i, val in enumerate(piece.split("\n")):
                    with self.term.location(padding + position, 1 + i):
                        print(self.theme.ws_top(val))
                position += max(len(p) for p in piece.split("\n"))

            # draw side characters
            for i, char in enumerate(ascii_art.FEN[: self.term.height - 2]):
                with self.term.location(0, 1 + i):
                    print(self.theme.ws_side_chars(char))
                with self.term.location(self.term.width, 1 + i):
                    print(self.theme.ws_side_chars(char))

            # draw box center message
            message = "PRESS ANY KEY TO START"
            padding = (self.term.width - len(message)) // 2
            with self.term.location(padding, self.term.height // 2):
                print(self.theme.ws_message(message))

            # draw THINK box
            padding = (self.term.width - len(ascii_art.THINK.split("\n")[0])) // 2
            for i, val in enumerate(ascii_art.THINK.split("\n")):
                with self.term.location(
                    5, self.term.height - len(ascii_art.THINK.split("\n")) + i
                ):
                    print(self.theme.ws_think(val))
            keypress = self.term.inkey()
            return keypress

    def show_game_menu(self) -> str:
        """Prints the game-menu screen."""

        def print_options() -> None:
            for i, option in enumerate(
                constants.MENU_MAPPING.items()
            ):  # updates the options
                title, (_, style, highlight) = option
                if i == self.curr_highlight:
                    print(
                        self.term.move_x(term_positions[i])
                        + getattr(self.theme, highlight)
                        + str(title)
                        + self.term.normal
                        + self.term.move_x(0),
                        end="",
                    )
                else:
                    print(
                        self.term.move_x(term_positions[i])
                        + getattr(self.theme, style)
                        + str(title)
                        + self.term.normal
                        + self.term.move_x(0),
                        end="",
                    )

            if self.curr_highlight != 9:
                print(
                    self.term.move_down(3)
                    + self.theme.gm_option_message
                    + self.term.center(
                        list(constants.MENU_MAPPING.values())[self.curr_highlight][0]
                    )
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

        w, h = self.term.width, self.term.height

        self.curr_highlight = 9
        spacing = int(w * 0.05)
        padding = (
            w
            - sum(len(option) for option in constants.MENU_MAPPING.keys())
            - spacing * len(constants.MENU_MAPPING.keys())
        ) // 2
        position = padding
        term_positions = []
        for option in constants.MENU_MAPPING:
            term_positions.append(position)
            position += len(option) + spacing

        title_split = ascii_art.menu_logo.rstrip().split("\n")
        max_chars = len(max(title_split, key=len))
        with self.term.cbreak(), self.term.hidden_cursor():
            print(self.term.home + self.term.clear + self.term.move_y(int(h * 0.10)))
            for component in title_split:  # Prints centered title
                component = (
                    str(component)
                    + " " * (max_chars - len(component))
                    + "  " * int(w * 0.03)
                )
                print(self.term.center(component))
            print(self.term.move_down(3))  # Sets the cursor to the options position
            print_options()
            while (
                pressed := self.term.inkey().name
            ) != "KEY_ENTER":  # Loops till the user chooses an option
                if pressed == "KEY_TAB":
                    select_option()
                    print_options()
        print(self.term.home + self.term.clear)  # Resets the terminal

        if not self.curr_highlight:
            return "NEW_LOBBY"
        elif self.curr_highlight == 1:
            return "CONNECT_TO_LOBBY"
        elif self.curr_highlight == 2:
            return "SETTINGS"
        else:
            return "EXIT"

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

    def get_piece_and_color(self, row: int, col: int) -> tuple:
        """Returns color and piece info of the cell."""
        if (row + col) % 2 == 0:
            bg = self.theme.themes[self.colour_scheme]["white_squares"]
        else:
            bg = self.theme.themes[self.colour_scheme]["black_squares"]
        piece, color = mapper[self.chess_board[row][col]]
        return (piece, color, bg)

    def is_valid_move(self, move: str) -> bool:
        """Checks if we are actually using our piece."""
        if len(move) != 2:
            return False
        col = move[0]
        row = move[1]
        if col.upper() not in COL or row not in ROW:
            return False
        col_index = COL.index(col.upper())
        row_index = len(self) - int(row)
        if self.white_move:
            return self.chess_board[row_index][col_index] in WHITE_PIECES
        return self.chess_board[row_index][col_index] in BLACK_PIECES

    @staticmethod
    def fen_to_board(fen: str) -> list:
        """Return the chess array representation of FEN."""
        board = []
        fen_parts = fen.split(" ")
        board_str = fen_parts[0]
        for i in board_str.split("/"):
            if len(i) == 8:
                board.append(["em" if _.isnumeric() else _ for _ in i])
            else:
                row = []
                for j in i:
                    if j.isnumeric():
                        row = row + ["em"] * int(j)
                    else:
                        row.append(j)
                board.append(row)
        return board

    def show_game_screen(self) -> None:
        """Shows the chess board."""
        print(self.term.home + self.term.clear)
        with self.term.hidden_cursor():
            for i in range(len(self)):
                # for every col we need to add number too!
                num = len(self) - i
                x = self.tile_width // 2
                y = i * self.tile_height + self.tile_height // 2
                with self.term.location(x, y):
                    print(num)
                for j in range(len(self)):
                    self.update_block(i, j)
            # adding Alphabets for columns
            for i in range(len(self)):
                with self.term.location(
                    x * 2 - 1 + i * self.tile_width, len(self) * self.tile_height
                ):
                    print(str.center(COL[i], len(self)))
            while True:
                # available_moves = chessboard.all_available_moves()
                start_move, end_move = self.handle_arrows()
                # print(start_move, end_move)
                with self.term.location(0, self.term.height - 10):
                    self.chess.move_piece("".join((*start_move, *end_move)).lower())
                    self.fen = self.chess.give_board()
                    self.chess_board = self.fen_to_board(self.fen)
                self.update_block(
                    len(self) - int(end_move[1]), COL.index(end_move[0].upper())
                )
                self.update_block(
                    len(self) - int(start_move[1]), COL.index(start_move[0].upper())
                )

    def update_block(self, row: int, col: int) -> None:
        """Updates block on row and col(we must first mutate actual list first)."""
        piece, color, bg = self.get_piece_and_color(row, col)
        if self.selected_row == row and self.selected_col == col:
            bg = self.theme.themes[self.colour_scheme]["selected_square"]
        elif [row, col] in self.possible_moves:
            bg = self.theme.themes[self.colour_scheme]["legal_squares"]
        self.draw_tile(
            self.tile_width + col * (self.tile_width + self.offset_x),
            row * (self.tile_height + self.offset_y),
            text=piece,
            fg=color,
            bg=bg,
        )

    @staticmethod
    def get_row_col(row: int, col: str) -> tuple:
        """Returns row and col index."""
        return (8 - int(row), COL.index(col.upper()))

    def get_possible_move(self, piece: str) -> list:
        """Gives possible moves for specific piece."""
        moves = self.chess.all_available_moves()
        piece = piece.lower()
        return [i for i in moves if piece in i]

    def highlight_moves(self, move: str) -> None:
        """Take a piece and highlights all possible moves."""
        old_moves = deepcopy(self.possible_moves)
        self.possible_moves = []
        # removes old moves
        for i in old_moves:
            self.update_block(i[0], i[1])
        # highlights the possible moves.
        piece = self.chess_board[self.selected_row][self.selected_col]
        if piece == "em":
            return
        for i in self.get_possible_move("".join(move)):
            x = len(self) - int(i[3])
            y = COL.index(i[2].upper())
            self.possible_moves.append([x, y])
            self.update_block(x, y)
        with self.term.location(0, self.term.height - 5):
            print(self.possible_moves)

    def handle_arrows(self) -> tuple:
        """Manages the arrow movement on board."""
        start_move = end_move = False
        while True:
            with self.term.cbreak():
                inp = self.term.inkey()
            input_key = repr(inp)
            if input_key == "KEY_DOWN":
                if self.selected_row < 7:
                    self.selected_row += 1
                    self.update_block(self.selected_row - 1, self.selected_col)
                    self.update_block(self.selected_row, self.selected_col)
            elif input_key == "KEY_UP":
                if self.selected_row > 0:
                    self.selected_row -= 1
                    self.update_block(self.selected_row + 1, self.selected_col)
                    self.update_block(self.selected_row, self.selected_col)
            elif input_key == "KEY_LEFT":
                if self.selected_col > 0:
                    self.selected_col -= 1
                    self.update_block(self.selected_row, self.selected_col + 1)
                    self.update_block(self.selected_row, self.selected_col)
            elif input_key == "KEY_RIGHT":
                if self.selected_col < 7:
                    self.selected_col += 1
                    self.update_block(self.selected_row, self.selected_col - 1)
                    self.update_block(self.selected_row, self.selected_col)
            elif input_key == "KEY_ENTER":
                move = self.chess_board[self.selected_row][self.selected_col]
                if not start_move:
                    # if clicked empty block
                    if move == "em":
                        continue
                    start_move = (
                        COL[self.selected_col],
                        ROW[len(self) - self.selected_row - 1],
                    )
                    self.highlight_moves(start_move)
                else:
                    # get what location is selected. eg A7
                    current_move = (
                        COL[self.selected_col],
                        ROW[len(self) - self.selected_row - 1],
                    )
                    if [self.selected_row, self.selected_col] in self.possible_moves:
                        end_move = (
                            COL[self.selected_col],
                            ROW[len(self) - self.selected_row - 1],
                        )
                        old_moves = deepcopy(self.possible_moves)
                        self.possible_moves = []
                        for i in old_moves:
                            self.update_block(i[0], i[1])
                        return start_move, end_move
                    else:
                        # special condition check.
                        # if enter key is pressed for another piece that can be moved
                        # change highligting to that piece
                        self.highlight_moves(current_move)
                        # this means the move is a valid move so we set it as start_move
                        if self.possible_moves:
                            start_move = current_move
                            continue
                        start_move = False
                        old_moves = deepcopy(self.possible_moves)
                        self.possible_moves = []
                        for i in old_moves:
                            self.update_block(i[0], i[1])

    def start_game(self) -> None:
        """
        Starts the chess game.

        TODO : check for net connection
        TODO: Check if console supported
        """
        if self.show_welcome_screen() == "q":
            print(self.term.clear + self.term.exit_fullscreen)
        else:
            # call show_game_menu
            menu_choice = self.show_game_menu()
            if menu_choice == "NEW_LOBBY":
                # make a new lobby
                self.show_game_screen()
            elif menu_choice == "CONNECT_TO_LOBBY":
                # connect to a lobby
                pass
            elif menu_choice == "SETTINGS":
                # open settings menu
                pass
            elif menu_choice == "EXIT":
                # exit the game peacefully
                print(self.term.clear + self.term.exit_fullscreen + self.term.clear)
