import json
import logging
import os.path
import socket
from copy import deepcopy
from typing import Optional

import httpx
from blessed import Terminal
from numpy import ones
from platformdirs import user_cache_dir
from websocket import (
    WebSocket,
    WebSocketBadStatusException,
)

from app import ascii_art
from app.chess import ChessBoard
from app.constants import ChessGame, Connections, Menu, WelcomeScreen
from app.ui.Colour import ColourScheme

mapper = {
    "em": ("", "white"),
    "K": (ChessGame.PIECES[0], "white"),
    "Q": (ChessGame.PIECES[1], "white"),
    "R": (ChessGame.PIECES[2], "white"),
    "B": (ChessGame.PIECES[3], "white"),
    "N": (ChessGame.PIECES[4], "white"),
    "P": (ChessGame.PIECES[5], "white"),
    "k": (ChessGame.PIECES[6], "black"),
    "q": (ChessGame.PIECES[7], "black"),
    "r": (ChessGame.PIECES[8], "black"),
    "b": (ChessGame.PIECES[9], "black"),
    "n": (ChessGame.PIECES[10], "black"),
    "p": (ChessGame.PIECES[11], "black"),
}

log = logging.getLogger(__name__)


class Player:
    """Class for defining a player."""

    def __init__(self, token: str = None):
        self.token = token
        self.player_id = None
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
        self.player = None
        self.game_id = None  # the game lobby id that the server will provide for online multiplayer

        self.api_url = Connections.API_URL
        self.ws_url = Connections.WEBSOCKET_URL
        self.headers = dict()
        self.web_socket = WebSocket()

        self.w = self.term.width
        self.h = self.term.height

        self.colour_scheme = "default"
        self.theme = ColourScheme(self.term, theme=self.colour_scheme)

        self.chess = ChessBoard(ChessGame.INITIAL_FEN)
        self.chess_board = self.fen_to_board(self.chess.give_board())
        self.fen = ChessGame.INITIAL_FEN

        self.tile_width = 6
        self.tile_height = 3

        # self.my_color = 'white' # for future
        self.white_move = True  # this will change in multiplayer game

        self.x_shift = int(self.w * 0.3)
        self.y_shift = int(self.h * 0.2)

        self.x = 0
        self.y = 0

        self.chat_enabled = False
        self.chat_box_width = self.w - int(self.w * 0.745) - 1
        self.chat_hist_height = 1
        self.full_chat_hist = ""
        self.chat_box_x = int(self.w * 0.70)

        self.selected_row = 6
        self.selected_col = 0
        self.possible_moves = []

        self.flag = True

        # self.handle_arrows()
        self.moves_played = 0
        self.moves_limit = 100  # TODO: MAKE THIS DYNAMIC
        self.visible_layers = 8

        self.screen = "fullscreen"
        self.hidden_layer = ones((self.visible_layers, self.visible_layers))
        self.king_check = False

    def __len__(self) -> int:
        return 8

    @staticmethod
    def check_network_connection(
        host: Optional[str] = "8.8.8.8",
        port: Optional[int] = 53,
        timeout: Optional[int] = 3,
    ) -> bool:
        """
        Ping google server IP and check whether the user has active network connection.

        Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP)
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as ex:
            print(ex)
            return False

    @staticmethod
    def ensure_terminal_size(terminal: Terminal) -> None:
        """Ensure that the terminal is sized so as to properly render the entire game."""
        t = terminal
        min_height = 33
        min_width = 133
        height, width = t.height, t.width
        midline = height // 2
        size_good = False
        while not size_good:
            if height >= min_height and width >= min_width:

                print(
                    t.clear
                    + t.move_y(midline)
                    + t.center("Nicely done! Hit [ENTER]] to continue...").rstrip()
                )
                while not size_good:
                    key = t.inkey()
                    if not key:
                        continue
                    elif key.name == "KEY_ENTER":
                        break
                size_good = True
            elif height < min_height:
                print(
                    t.clear
                    + t.move_y(midline)
                    + t.center(
                        "Please increase the height of your terminal window!"
                    ).rstrip()
                )
                while height == t.height:
                    pass
                height = t.height
            elif width < min_width:
                print(
                    t.clear
                    + t.move_y(midline)
                    + t.center(
                        "Please increase the width of your terminal window!"
                    ).rstrip()
                )
                while width == t.width:
                    pass
                width = t.width
            midline = height // 2
        return

    def ask_or_get_token(self) -> str:
        """
        Ask the user/get token from cache.

        If token is found in user's cache then read that else ask
        the user for the token, validate it through the API and store it
        in user's cache.
        """
        cache_path = f'{user_cache_dir("stealth_chess")}/token.json'
        if os.path.exists(cache_path):
            # Read file token from file as cache exists
            with open(cache_path, "r", encoding="utf-8") as file:
                token = (json.load(file)).get("token")
                if token:
                    return token

        # If cache file is not found
        token_ok = False
        token = input("Enter your API token")
        while not token_ok:
            r = httpx.put(
                f"{self.api_url}/validate_token",
                json={"token": token},
            )
            if r.status_code != 200:
                token = input("Invalid token, enter the correct one: ")
            else:
                token_ok = True

        token = {"token": token}  # ask token

        # Make the cache folder for storing the token
        directory = os.path.dirname(cache_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Write the token to cache file
        with open(cache_path, "w+", encoding="utf-8") as file:
            json.dump(token, file, ensure_ascii=False, indent=4)
        return token["token"]

    def create_lobby(self) -> str:
        """Used to create a game lobby on the server or locally."""
        if not self.game_id:
            try:
                if not self.check_network_connection():
                    return f"{self.term.blink}Can't connect to internet"
                httpx.get(self.api_url)
            except httpx.ConnectError:
                return f"{self.term.blink}Can't connect to {self.api_url}"

            # server up
            try:
                token = self.ask_or_get_token()
            except KeyboardInterrupt:
                return "BACK"

            self.player = Player(token)
            # get the game id
            self.headers.update({"Authorization": f"Bearer {self.player.token}"})
            resp = ""
            url = f"{self.api_url}/game/new"

            try:
                resp = httpx.get(url, headers=self.headers)
                if resp.status_code != 200:
                    return f"server returned Error code {resp.status_code}"
                self.game_id = resp.json()["room"]
                return "New lobby created Press [ENTER] to continue"
            except httpx.HTTPError:
                print(url)
                raise
            except httpx.ReadTimeout:
                print(url)
                raise
        else:
            return "Restart Game ..."

    def connect_to_lobby(self) -> str:
        """Connect to a lobby after Creating one or with game_id."""
        if not self.game_id:
            self.game_id = input("Enter Game id :- ").strip()
        if not self.player:
            self.player = Player(self.ask_or_get_token())
            self.headers = {"Authorization": f"Bearer {self.player.token}"}

        ws_url = f"{self.ws_url}/game/{self.game_id}"
        data = ""
        try:
            self.web_socket.connect(ws_url, header=self.headers)
            data = "INFO::INIT"
            print(self.term.home + self.theme.background + self.term.clear)
            print(f"lobby id :- {self.game_id}")
            print("Waiting for all players to connect ....")

            while data[1] != "READY":
                data = self.web_socket.recv().split("::")
                if data[1] == "PLAYER":  # INFO::PLAYER::p1
                    self.player.player_id = int(data[2][-1])
                    print(self.player.player_id)

            return "READY"

        except WebSocketBadStatusException:
            return "Sever Error pls.. Try Again...."
        except Exception:
            log.error(f"{data} {ws_url}")
            raise

    def show_welcome_screen(self) -> str:
        """
        Prints startup screen and return pressed key.

        Draws the ASCII chess pieces on the top/bottom of the terminal.
        """
        with self.term.cbreak():
            print(self.term.home + self.theme.background + self.term.clear)

            # draw bottom chess pieces
            padding = (
                self.term.width
                - sum(
                    max(len(p) for p in piece.split("\n"))
                    for piece in WelcomeScreen.GAME_WELCOME_TOP
                )
            ) // 2
            position = 0
            for piece in WelcomeScreen.GAME_WELCOME_TOP:
                for i, val in enumerate(piece.split("\n")):
                    with self.term.location(
                        padding + position,
                        self.term.height - (len(piece.split("\n")) + 1) + i,
                    ):
                        print(self.theme.ws_bottom(val))
                position += max(len(p) for p in piece.split("\n"))

            # draw top chess pieces
            position = 0
            for piece in WelcomeScreen.GAME_WELCOME_BOTTOM:
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
        """
        Main game menu.

        This is the main game menu showing all the four possible options i.e.
        Create Game, Join Game, settings and exit. Each have a description which
        can be rendered on pressing `KEY_TAB`.
        """

        def print_options() -> None:
            for i, option in enumerate(
                Menu.MENU_MAPPING.items()
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
                        list(Menu.MENU_MAPPING.values())[self.curr_highlight][0]
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
            - sum(len(option) for option in Menu.MENU_MAPPING.keys())
            - spacing * len(Menu.MENU_MAPPING.keys())
        ) // 2
        position = padding
        term_positions = []
        for option in Menu.MENU_MAPPING:
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

            # Loop till the user chooses an option or presses tab to show the description
            while (pressed := self.term.inkey().name) != "KEY_ENTER":
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

    def chess_status_display(
        self,
        start: str = "",
        end: str = "",
        x_pos: int = 0,
        y_pos: int = 0,
        y_pos_box: int = 0,
        box_width: int = 20,
        title: str = "Your Previous move",
        content: str = "",
        is_last_move: bool = True,
    ) -> None:
        """Function to display previous move plus additional box creator."""
        if is_last_move:
            y_pos_box = int(self.h * 0.3)
        if len(title) > box_width:
            box_width = len(title) + 2
        """Prints the previous move of the player."""
        print(
            self.term.black_on_white
            + self.term.move_xy(self.w // 13, y_pos_box)
            + "╭"
            + "─" * box_width
            + "╮"
        )
        space_right = (box_width - len(title)) // 2
        space_left = box_width - len(title) - space_right
        print(
            self.term.move_x(self.w // 13)
            + "│"
            + " " * space_left
            + title
            + " " * space_right
            + "│"
        )
        print(self.term.move_x(self.w // 13) + "├" + "─" * box_width + "┤")  # 21

        if is_last_move:
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
        else:
            space_right = (box_width - len(content)) // 2
            space_left = box_width - len(content) - space_right - 1
            print(
                self.term.move_x(self.w // 13)
                + "│"
                + " " * space_left
                + " "
                + content
                + " " * space_right
                + "│"
            )
        print(
            self.term.move_x(self.w // 13)
            + "╰"
            + "─" * box_width
            + "╯"
            + self.term.normal
        )

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
            if length < width:
                content = self.term.green + content[:4] + self.term.yellow + content[4:]
            elif 4 - (length - width) >= 0:
                content = (
                    self.term.green
                    + content[: 4 - (length - width)]
                    + self.term.yellow
                    + content[4 - (length - width) :]
                )
            else:
                content = self.term.yellow + content
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
        text = self.term.green + text[:4] + self.term.yellow + text[4:]
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
            text_prefix = "YOU:"
            text = ""
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
                        text=text_prefix + text,
                    )
                if flag == "KEY_BACKSPACE":
                    text = text[: len(text) - 1]
                    self.box(
                        height=1,
                        width=self.chat_box_width,
                        x_pos=self.chat_box_x,
                        y_pos=self.h - 4,
                        visibility_dull=False,
                        text=text_prefix + text,
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
                self.chatbox_history(text=text_prefix + text)  # Send the message
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
        """Draws a single chess tile and prints the `text` in the middle of it."""
        style = getattr(self.term, f"{fg}_on_{bg}")
        for j in range(y, y + self.tile_height):
            for i in range(x, x + self.tile_width):
                with self.term.location(i + x_offset, j + y_offset):
                    print(style(" "))
        with self.term.location(x + x_offset, y + y_offset + (self.tile_height // 2)):
            print(style(str.center(text, self.tile_width)))

    def get_piece_meta(self, row: int, col: int) -> tuple:
        """Get colour and piece information of the cell."""
        if (row + col) % 2 == 0:
            bg = self.theme.themes[self.colour_scheme]["white_squares"]
        else:
            bg = self.theme.themes[self.colour_scheme]["black_squares"]
        piece_value = self.chess_board[row][col]
        piece, color = mapper[piece_value]
        return (piece, color, bg)

    @staticmethod
    def fen_to_board(fen: str) -> list:
        """Convert the chess array to a FEN representation of it."""
        board = []
        fen_parts = fen.split(" ")
        board_str = fen_parts[0]
        for i in board_str.split("/"):
            if len(i) == 8:
                board.append(["em" if _.isnumeric() else _ for _ in i])
            else:
                row = []
                for j in i:
                    # numeric is when the chess tile is empty
                    # `em` points to empty chess tile
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
            inp = self.term.inkey()
            if inp in ("q", "Q"):
                self.show_game_menu()
            else:
                self.__init__()
                self.show_game_screen()

    def print_message(self, message: str, content: Optional[str] = "") -> None:
        """Display message in the screen. For example CHECK, CHECKMATE."""
        # need to change the position of the message
        self.chess_status_display(
            y_pos_box=int(self.h * 0.4 + 2),
            title=message,
            content=content,
            box_width=20,
            is_last_move=False,
        )

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
            # Adding Alphabets to indicate columns
            for i in range(len(self)):
                with self.term.location(
                    x * 2 - 1 + i * self.tile_width + self.x_shift,
                    len(self) * self.tile_height + self.y_shift + 1,
                ):
                    print(str.center(ChessGame.COL[i], len(self)))

            try:
                self.web_socket.send("BOARD::GET_BOARD")
                no = True
                while no:
                    data = self.web_socket.recv().split("::")
                    self.chess.set_fen(data[2])
                    self.fen = self.chess.give_board()
                    no = False
            except Exception:
                print(data)
                raise

            while True:
                # available_moves = chessboard.all_available_moves()
                # get the latest board
                if self.player.player_id == 1:
                    self.player_1_update()
                elif self.player.player_id == 2:
                    self.player_2_update()

                start_move, end_move = self.handle_arrows()
                move = "".join((*start_move, *end_move)).lower()
                self.render_board(start_move, end_move)

                # update the server
                self.web_socket.send(f"BOARD::MOVE::{move}")
                try:
                    data = [""]
                    self.web_socket.send("BOARD::GET_BOARD")
                    while data[0] != "BOARD":
                        data = self.web_socket.recv().split("::")
                    self.chess.set_fen(data[2])
                except Exception:
                    print(data)
                    raise

    def player_1_update(self) -> None:
        """Function to get the latest FEN from the server after P2 makes a move."""
        if not self.is_white_turn():  # the last move was made by black (p2)
            new_board = False
            while not new_board:  # wait till server broadcasts the new FEN string
                data = self.web_socket.recv().split("::")
                # todo add Waiting for enemy to make a move GUI here for player 1
                if data[0] == "BOARD" and data[1] == "BOARD":
                    if self.is_white_turn(data[2]):
                        self.chess.set_fen(data[2])
                        self.fen = self.chess.give_board()
                        self.chess_board = self.fen_to_board(self.fen)
                        self.update_board()
                        new_board = True

    def player_2_update(self) -> None:
        """Function to get the latest FEN from the server after P1 makes a move."""
        if self.is_white_turn():  # the last move was made by white (p1)
            new_board = False
            while not new_board:  # wait till server broadcasts the new FEN string
                data = self.web_socket.recv().split("::")
                # todo add Waiting for enemy to make a move GUI here for player 2
                if data[0] == "BOARD" and data[1] == "BOARD":
                    if not self.is_white_turn(data[2]):
                        self.chess.set_fen(data[2])
                        self.fen = self.chess.give_board()
                        self.chess_board = self.fen_to_board(self.fen)
                        self.update_board()
                        new_board = True

    def render_board(self, start_move: list, end_move: list) -> None:
        """
        Renders the board on the terminal.

        updating only the place where the move was made and not the whole screen
        """
        # with self.term.location(0, self.term.height - 10):
        move = "".join((*start_move, *end_move)).lower()
        self.chess.move_piece(move)
        self.king_check = False

        content = "WHITEs MOVE" if not self.is_white_turn() else "BLACKs MOVE"
        self.print_message("STATUS", content=content)

        self.fen = self.chess.give_board()
        self.chess_board = self.fen_to_board(self.fen)
        self.chess_status_display(
            start="".join(start_move),
            end="".join(end_move),
            x_pos=ChessGame.COL.index(end_move[0].upper()),
            y_pos=8 - int(end_move[1]),
        )
        if move in ChessGame.POSSIBLE_CASTLING_MOVES:
            self.update_board()
            return
        self.update_block(
            len(self) - int(end_move[1]), ChessGame.COL.index(end_move[0].upper())
        )
        self.update_block(
            len(self) - int(start_move[1]), ChessGame.COL.index(start_move[0].upper())
        )
        self.moves_played += 1
        if self.get_game_status() == ChessGame.STATUS["CHECKMATE"]:
            self.print_message(
                "CHECKMATE. GAME OVER",
                content="PRESS Q TO EXIT",
            )
            self.show_game_over()
        elif self.get_game_status() == ChessGame.STATUS["CHECK"]:
            self.print_message("CHECK", content="PLAY YOUR KING")
            self.highlight_check()
            self.king_check = True

        self.update_block(
            len(self) - int(end_move[1]), ChessGame.COL.index(end_move[0].upper())
        )
        self.update_block(
            len(self) - int(start_move[1]),
            ChessGame.COL.index(start_move[0].upper()),
        )
        self.moves_played += 1

        if self.moves_played % self.moves_limit == 0 and self.visible_layers > 2:
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
        visible_pieces = (
            ChessGame.WHITE_PIECES
            if self.player.player_id == 1
            else ChessGame.BLACK_PIECES
        )
        make_invisible = (
            self.hidden_layer[row][col] == 0
            and not self.chess_board[row][col] in visible_pieces
        )
        if make_invisible:
            piece = " "

        self.draw_tile(
            self.tile_width + col * self.tile_width,
            row * self.tile_height,
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
        """Get the row and col index."""
        return (8 - int(row), ChessGame.COL.index(col.upper()))

    def get_possible_move(self, piece: str) -> list:
        """Gives all possible moves for the given piece."""
        moves = self.chess.all_available_moves()
        piece = piece.lower()
        return [i for i in moves if piece in i]

    def is_white_turn(self, fen: str = None) -> bool:
        """Returns if it's white's turn."""
        if fen:
            fen_parts = fen.split(" ")
        else:
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
            # If there are no possible moves for the piece
            return

        for i in self.get_possible_move("".join(move)):
            x = len(self) - int(i[3])
            y = ChessGame.COL.index(i[2].upper())
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
                        move in ChessGame.WHITE_PIECES
                        if self.is_white_turn()
                        else move in ChessGame.BLACK_PIECES
                    )
                    if not is_valid:
                        continue
                    start_move = (
                        ChessGame.COL[self.selected_col],
                        ChessGame.ROW[len(self) - self.selected_row - 1],
                    )
                    self.highlight_moves(start_move)

                else:
                    if [self.selected_row, self.selected_col] in self.possible_moves:
                        end_move = (
                            ChessGame.COL[self.selected_col],
                            ChessGame.ROW[len(self) - self.selected_row - 1],
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
                            move in ChessGame.WHITE_PIECES
                            if self.is_white_turn()
                            else move in ChessGame.BLACK_PIECES
                        )
                        if is_same_color:
                            start_move = (
                                ChessGame.COL[self.selected_col],
                                ChessGame.ROW[len(self) - self.selected_row - 1],
                            )
                            end_move = False
                            self.highlight_moves(start_move)
                            continue
                        start_move = False
                        end_move = False
                        self.highlight_moves(start_move)
            if self.king_check:
                self.highlight_check()

    def reset_class(self) -> None:
        """Reset player game room info."""
        self.game_id = None
        self.player.player_id = None

    def start_game(self) -> None:
        """Starts the chess game."""
        self.ensure_terminal_size(self.term)
        if self.show_welcome_screen() == "q":
            print(self.term.clear + self.term.exit_fullscreen)
        else:
            # call show_game_menu
            menu_choice = "NO_EXIT"
            while menu_choice != "EXIT":
                if self.player:
                    self.reset_class()
                menu_choice = self.show_game_menu()
                if menu_choice == "NEW_LOBBY":
                    # make a new lobby
                    print(self.create_lobby())
                    resp = self.connect_to_lobby()
                    if resp != "READY":
                        print(resp)
                elif menu_choice == "CONNECT_TO_LOBBY":
                    # connect to a lobby
                    resp = self.connect_to_lobby()
                    if resp != "READY":
                        print(resp)
                elif menu_choice == "SETTINGS":
                    # open settings menu
                    pass
                print(self.term.home + self.theme.background + self.term.clear)
                if self.player.player_id:
                    try:
                        self.show_game_screen()
                    except Exception as e:
                        print(e)
                        raise
            # exit the game peacefully
            self.web_socket.close()
            print(self.term.clear + self.term.exit_fullscreen + self.term.clear)
