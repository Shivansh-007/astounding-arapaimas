from copy import deepcopy

from blessed import Terminal
from numpy import ones

from app import ascii_art
from app.chess import ChessBoard
from app.constants import (
    BLACK_PIECES,
    CHESS_STATUS,
    COL,
    GAME_WELCOME_BOTTOM,
    GAME_WELCOME_TOP,
    INITIAL_FEN,
    MENU_MAPPING,
    PIECES,
    POSSIBLE_CASTLING_MOVES,
    ROW,
    WHITE_PIECES,
)
from app.ui.Colour import ColourScheme

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
        self.w = self.term.width
        self.h = self.term.height
        # TODO:: USE THIS
        self.players = None
        # TODO:: USE THIS
        self.game_id = None  # the game lobby id that the server will provide for online multiplayer
        # TODO:: USE THIS
        self.server_ip = None
        self.colour_scheme = "default"
        self.theme = ColourScheme(self.term, theme=self.colour_scheme)
        self.chess = ChessBoard(INITIAL_FEN)
        self.chess_board = self.fen_to_board(self.chess.give_board())
        self.fen = INITIAL_FEN
        self.tile_width = 6
        self.tile_height = 3
        # TODO:: REMOVE THESE 2 if they're gonna be 0(they are used for spaces b/w tiles)
        self.offset_x = 0
        self.offset_y = 0
        self.x_shift = int(self.w * 0.3)
        self.y_shift = int(self.h * 0.2)
        self.x = 0
        self.y = 0
        self.chat_enabled = False
        # self.my_color = 'white' # for future
        self.selected_row = 6
        self.selected_col = 0
        self.possible_moves = []
        self.flag = True
        self.chat_box_width = self.w - int(self.w * 0.745) - 1
        self.chat_hist_height = 1
        self.full_chat_hist = ""
        self.chat_box_x = int(self.w * 0.73)
        # self.term.number_of_colors = 256
        # self.handle_arrows()
        self.moves_played = 0
        self.moves_limit = 100  # TODO:: MAKE THIS DYNAMIC
        self.visible_layers = 8
        self.hidden_layer = ones((self.visible_layers, self.visible_layers))
        self.king_check = False

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
                    max(len(p) for p in piece.split("\n")) for piece in GAME_WELCOME_TOP
                )
            ) // 2
            position = 0
            for piece in GAME_WELCOME_TOP:
                for i, val in enumerate(piece.split("\n")):
                    with self.term.location(
                        padding + position,
                        self.term.height - (len(piece.split("\n")) + 1) + i,
                    ):
                        print(self.theme.ws_bottom(val))
                position += max(len(p) for p in piece.split("\n"))

            # draw top chess pieces
            position = 0
            for piece in GAME_WELCOME_BOTTOM:
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
            for i, option in enumerate(MENU_MAPPING.items()):  # updates the options
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
                        list(MENU_MAPPING.values())[self.curr_highlight][0]
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
            - sum(len(option) for option in MENU_MAPPING.keys())
            - spacing * len(MENU_MAPPING.keys())
        ) // 2
        position = padding
        term_positions = []
        for option in MENU_MAPPING:
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

    def show_prev_move(self, start: list, end: list, x_pos: int, y_pos: int) -> None:
        """Prints the previous move of the player."""
        print(
            self.term.black_on_white
            + self.term.move_xy(self.w // 13, int(self.h / 2.4))
            + "╭"
            + "─" * 20
            + "╮"
        )
        print(self.term.move_x(self.w // 13) + "│ Your Previous move │")
        print(self.term.move_x(self.w // 13) + "├" + "─" * 20 + "┤")  # 21
        print(
            self.term.move_x(self.w // 13)
            + "│"
            + " " * 3
            + mapper[self.chess_board[y_pos][x_pos]][0]
            + " "
            + start
            + " ==> "
            + end
            + " " * 6
            + "│"
        )
        print(self.term.move_x(self.w // 13) + "╰" + "─" * 20 + "╯" + self.term.normal)

    def box(
        self,
        height: int = 3,
        width: int = 20,
        x_pos: int = 0,
        y_pos: int = 0,
        visibility_dull: bool = True,
        text: str = "",
        no_checks: bool = False,
        shift_y: int = 1,
    ) -> None:
        """Handles creation of tables and printing text in it."""
        length = len(text)
        color = self.term.color_rgb(100, 100, 100)
        if not visibility_dull:
            color = self.term.white
        if not no_checks and length > width:
            content = text[length - width : length]
        else:
            content = text
        print(color + self.term.move_xy(x_pos, y_pos))
        print(self.term.move_x(x_pos) + "╭" + "─" * width + "╮")
        for _ in range(height):
            print(self.term.move_x(x_pos) + "│" + " " * width + "│")
        print(self.term.move_up)
        if not no_checks:
            print(
                self.term.move_down(1)
                + self.term.move_x(x_pos)
                + "╰"
                + "─" * width
                + "╯"
                + self.term.move_x(0)
                + self.term.move_up
            )
        print(
            self.term.move_x(x_pos + 1)
            + self.term.move_up(shift_y)
            + self.term.yellow
            + content
            + self.term.normal
        )

    def chatbox_history(self, text: str) -> None:
        """Manages chat history to be displayed."""
        if len(text) > self.chat_box_width:
            self.chat_hist_height += (len(text)) // self.chat_box_width
        formatted_text = ""
        for i, char in enumerate(text):
            if (i + 1) % self.chat_box_width == 0:
                formatted_text += "\n" + self.term.move_x(self.chat_box_x + 1) + char
            else:
                formatted_text += char

        self.chat_hist_height += 1
        self.full_chat_hist += (
            formatted_text + "\n" + self.term.move_x(self.chat_box_x + 1)
        )
        self.box(
            height=(1 + self.chat_hist_height),
            width=self.chat_box_width,
            x_pos=self.chat_box_x,
            y_pos=self.h - 6 - self.chat_hist_height,
            visibility_dull=True,
            text=self.full_chat_hist,
            no_checks=True,
            shift_y=self.chat_hist_height,
        )

    def chatbox(self) -> None:
        """Creates chat box for the players."""
        self.box(
            height=1,
            width=self.chat_box_width,
            x_pos=self.chat_box_x,
            y_pos=self.h - 4,
            visibility_dull=False,
        )
        with self.term.cbreak():
            flag = ""
            text = "ME:"
            char = ""
            while flag != "KEY_ENTER" and flag != "KEY_TAB":
                if (
                    char is not None
                    and len(char.lower()) == 1
                    and flag != "KEY_BACKSPACE"
                ):
                    text += char.lower()
                    self.box(
                        height=1,
                        width=self.chat_box_width,
                        x_pos=self.chat_box_x,
                        y_pos=self.h - 4,
                        visibility_dull=False,
                        text=text,
                    )
                if flag == "KEY_BACKSPACE":
                    text = text[: len(text) - 1]
                    self.box(
                        height=1,
                        width=self.chat_box_width,
                        x_pos=self.chat_box_x,
                        y_pos=self.h - 4,
                        visibility_dull=False,
                        text=text,
                    )
                char = self.term.inkey()
                flag = char.name
            if flag == "KEY_ENTER":
                self.box(
                    height=1,
                    width=self.chat_box_width,
                    x_pos=self.chat_box_x,
                    y_pos=self.h - 4,
                    visibility_dull=True,
                )
                self.chatbox_history(text=text)  # Send the message
            else:
                self.box(
                    height=1,
                    width=self.chat_box_width,
                    x_pos=self.chat_box_x,
                    y_pos=self.h - 4,
                    visibility_dull=True,
                )
        print(self.term.hide_cursor + self.term.move_up)

    def draw_tile(
        self,
        x: int = 0,
        y: int = 0,
        x_offset: int = 0,
        y_offset: int = 0,
        text: str = None,
        fg: str = "black",
        bg: str = "white",
    ) -> None:
        """Draws one tile and text inside of it."""
        style = getattr(self.term, f"{fg}_on_{bg}")
        for j in range(y, y + self.tile_height):
            for i in range(x, x + self.tile_width):
                with self.term.location(i + x_offset, j + y_offset):
                    print(style(" "))
        with self.term.location(x + x_offset, y + y_offset + (self.tile_height // 2)):
            print(style(str.center(text, self.tile_width)))

    def get_piece_meta(self, row: int, col: int) -> tuple:
        """Returns color and piece info of the cell."""
        if (row + col) % 2 == 0:
            bg = self.theme.themes[self.colour_scheme]["white_squares"]
        else:
            bg = self.theme.themes[self.colour_scheme]["black_squares"]
        piece_value = self.chess_board[row][col]
        piece, color = mapper[piece_value]
        return (piece, color, bg)

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

    def get_game_status(self) -> int:
        """Get status of board."""
        return self.chess.board.status

    def show_game_over(self) -> None:
        """Display game over after checkmate."""
        # end the game and return to game_menu
        with self.term.cbreak():
            self.print_message("PRESS Q TO EXIT, ANY OTHER KEY TO RESTART")
            inp = self.term.inkey()
            if inp in ("q", "Q"):
                self.show_game_menu()
            else:
                self.show_game_screen()

    def print_message(self, message: str) -> None:
        """Display message in the screen. For example CHECK, CHECKMATE."""
        # need to change the position of the message
        with self.term.location(50, 10):
            print(self.theme.game_message, message)

    def highlight_check(self) -> None:
        """Higligh king if its CHECK."""
        for i, row in enumerate(self.chess_board):
            for j, col in enumerate(row):
                if (col == "K" and self.is_white_turn()) or (
                    col == "k" and not self.is_white_turn()
                ):
                    piece, color, _ = self.get_piece_meta(i, j)
                    self.draw_tile(
                        self.tile_width + j * (self.tile_width + self.offset_x),
                        i * (self.tile_height + self.offset_y),
                        self.x_shift,
                        self.y_shift,
                        text=piece,
                        fg=color,
                        bg=self.theme.themes[self.colour_scheme]["check"],
                    )
                    break

    def show_game_screen(self) -> None:
        """Shows the chess board."""
        print(self.term.home + self.term.clear + self.theme.background)
        self.box(
            height=1,
            width=self.chat_box_width,
            x_pos=self.chat_box_x,
            y_pos=self.h - 4,
            visibility_dull=True,
        )

        with self.term.hidden_cursor():
            for i in range(len(self)):
                # Adding Numbers to indicate rows
                num = len(self) - i
                x = self.tile_width // 2
                y = i * self.tile_height + self.tile_height // 2
                with self.term.location(x + self.x_shift, y + self.y_shift):
                    print(num)

                for j in range(len(self)):
                    self.update_block(i, j)
            # Adding Numbers to indicate columns
            for i in range(len(self)):
                with self.term.location(
                    x * 2 - 1 + i * self.tile_width + self.x_shift,
                    len(self) * self.tile_height + self.y_shift + 1,
                ):
                    print(str.center(COL[i], len(self)))
            while True:
                # self.print_message(' '*10)
                start_move, end_move = self.handle_arrows()
                with self.term.location(0, self.term.height - 10):
                    move = "".join((*start_move, *end_move)).lower()
                    self.chess.move_piece(move)
                    self.king_check = False

                    self.fen = self.chess.give_board()
                    self.chess_board = self.fen_to_board(self.fen)
                    self.show_prev_move(
                        start="".join(start_move),
                        end="".join(end_move),
                        x_pos=COL.index(end_move[0].upper()),
                        y_pos=8 - int(end_move[1]),
                    )
                if move in POSSIBLE_CASTLING_MOVES:
                    self.update_board()
                    continue
                self.update_block(
                    len(self) - int(end_move[1]), COL.index(end_move[0].upper())
                )
                self.update_block(
                    len(self) - int(start_move[1]), COL.index(start_move[0].upper())
                )
                self.moves_played += 1
                if self.get_game_status() == CHESS_STATUS["CHECKMATE"]:
                    self.print_message("THATS CHECKMATE!")
                    self.show_game_over()
                elif self.get_game_status() == CHESS_STATUS["CHECK"]:
                    # TODO:: NOTIFY KING
                    # print('WE ENTERED TO UPDATE ALL')
                    self.print_message("CHECK DUDE")
                    self.highlight_check()
                    self.king_check = True
                if (
                    self.moves_played % self.moves_limit == 0
                    and self.visible_layers > 2
                ):
                    self.visible_layers -= 2
                    invisible_layers = (8 - self.visible_layers) // 2
                    self.hidden_layer[0:invisible_layers, :] = 0
                    self.hidden_layer[-invisible_layers:, :] = 0
                    self.hidden_layer[:, 0:invisible_layers] = 0
                    self.hidden_layer[:, -invisible_layers:] = 0
                    self.update_board()

    def update_block(self, row: int, col: int) -> None:
        """Updates block on row and col(we must first mutate actual list first)."""
        piece, color, bg = self.get_piece_meta(row, col)
        if self.selected_row == row and self.selected_col == col:
            bg = self.theme.themes[self.colour_scheme]["selected_square"]
        elif [row, col] in self.possible_moves:
            bg = self.theme.themes[self.colour_scheme]["legal_squares"]
        if self.flag:
            self.flag = False
        make_invisible = (
            self.hidden_layer[row][col] == 0
            and not self.chess_board[row][col] in WHITE_PIECES
        )
        if make_invisible:
            piece = " "

        self.draw_tile(
            self.tile_width + col * (self.tile_width + self.offset_x),
            row * (self.tile_height + self.offset_y),
            self.x_shift,
            self.y_shift,
            text=piece,
            fg=color,
            bg=bg,
        )

    def update_board(self) -> None:
        """Updates whole board when needed. Simplest Solution but expensive."""
        for i in range(8):
            for j in range(8):
                self.update_block(i, j)

    @staticmethod
    def get_row_col(row: int, col: str) -> tuple:
        """Returns row and col index."""
        return (8 - int(row), COL.index(col.upper()))

    def get_possible_move(self, piece: str) -> list:
        """Gives possible moves for specific piece."""
        moves = self.chess.all_available_moves()
        piece = piece.lower()
        return [i for i in moves if piece in i]

    def is_white_turn(self) -> bool:
        """Returns if it's white's turn."""
        fen_parts = self.fen.split(" ")
        return fen_parts[1] == "w"

    def highlight_moves(self, move: str) -> None:
        """Take a piece and highlights all possible moves."""
        old_moves = deepcopy(self.possible_moves)
        self.possible_moves = []
        # removes old moves
        for i in old_moves:
            self.update_block(i[0], i[1])
        if not move:
            return
        # highlights the possible moves.
        piece = self.chess_board[self.selected_row][self.selected_col]
        if piece == "em":
            return
        for i in self.get_possible_move("".join(move)):
            x = len(self) - int(i[3])
            y = COL.index(i[2].upper())
            self.possible_moves.append([x, y])
            self.update_block(x, y)

    def handle_arrows(self) -> tuple:
        """Manages the arrow movement on board."""
        start_move = end_move = False
        while True:
            print(
                self.term.color_rgb(100, 100, 100)
                + self.term.move_xy(self.chat_box_x + 1, self.h - 2)
                + "Press [TAB] to message your opponent"
            )
            with self.term.cbreak():
                inp = self.term.inkey()
            if inp.name == "KEY_TAB":
                self.chatbox()
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
                    is_valid = (
                        move in WHITE_PIECES
                        if self.is_white_turn()
                        else move in BLACK_PIECES
                    )
                    if not is_valid:
                        continue
                    start_move = (
                        COL[self.selected_col],
                        ROW[len(self) - self.selected_row - 1],
                    )
                    self.highlight_moves(start_move)
                else:
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
                        if move == "em":
                            start_move = False
                            end_move = False
                            self.highlight_moves(start_move)
                            continue
                        is_same_color = (
                            move in WHITE_PIECES
                            if self.is_white_turn()
                            else move in BLACK_PIECES
                        )
                        if is_same_color:
                            start_move = (
                                COL[self.selected_col],
                                ROW[len(self) - self.selected_row - 1],
                            )
                            end_move = False
                            self.highlight_moves(start_move)
                            continue
                        start_move = False
                        end_move = False
                        self.highlight_moves(start_move)
            if self.king_check:
                self.highlight_check()

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
