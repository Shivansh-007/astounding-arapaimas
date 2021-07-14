from copy import deepcopy

from app.chess import ChessBoard
from blessed import Terminal

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

WHITE_PIECES = ("r", "n", "b", "q", "k", "p")

BLACK_PIECES = ("R", "N", "B", "Q", "K", "P")

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
        # self.handle_arrows()

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
        """Prints the screen to choose to play online or offline."""
        pass

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
        """Returns color and piece info of tyhe cell."""
        if (row + col) % 2 == 0:
            bg = "blue"
        else:
            bg = "green"
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

    def show_game_screen(self) -> None:
        """Shows the chess board."""

        def fen_to_board(a: str) -> list:
            b = []
            for index, item in enumerate(a.split(" ")):
                if index == 0:
                    for i in item.split("/"):
                        if len(i) == 8:
                            b.append(["em" if _.isnumeric() else _ for _ in i])
                        else:
                            r = []
                            for j in i:
                                if j.isnumeric():
                                    r = r + ["em"] * int(j)
                                else:
                                    r.append(j)
                            b.append(r)
                else:
                    b.append(item)
            return b

        print(self.term.fullscreen())
        print(self.term.home + self.term.clear)
        chessboard = ChessBoard(INITIAL_FEN)
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
            with self.term.location(0, self.term.height - 10):
                # current_moves = [
                #     move[2:]
                #     for move in available_moves
                #     if (start_move[0] + start_move[1]).lower() == move[:2]
                # ]

                chessboard.move_piece("".join((*start_move, *end_move)).lower())
                self.fen = chessboard.give_board()
                self.chess_board = fen_to_board(self.fen)
            print(8 - int(end_move[1]), COL.index(end_move[0].upper()))
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
            bg = "red"
        self.draw_tile(
            self.tile_width + col * (self.tile_width + self.offset_x),
            row * (self.tile_height + self.offset_y),
            text=piece,
            fg=color,
            bg=bg,
        )

    def handle_arrows(self) -> tuple:
        """Manages the arrow movement on board."""
        start_move = end_move = False
        while True:
            with self.term.cbreak(), self.term.hidden_cursor():
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
                if not start_move:
                    start_move = (
                        COL[self.selected_col],
                        ROW[len(self) - self.selected_row - 1],
                    )
                else:
                    end_move = (
                        COL[self.selected_col],
                        ROW[len(self) - self.selected_row - 1],
                    )
                    return start_move, end_move

    def start_game(self) -> None:
        """Starts the chess game."""
        pass
