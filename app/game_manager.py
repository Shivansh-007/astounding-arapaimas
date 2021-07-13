from blessed import Terminal

PIECES = "".join(chr(9812 + x) for x in range(12))
ROW = ["A", "B", "C", "D", "E", "F", "G", "H"]
COL = list(map(str, range(1, 9)))


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
        self.chess_board = None
        self.tile_width = 6
        self.tile_height = 3
        self.offset_x = 0
        self.offset_y = 0
        self.x = 0
        self.y = 0

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
        with self.term.location(
            x + (self.tile_width // 2) - 1, y + (self.tile_height // 2)
        ):
            print(style(text))

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
                    fg = "black"
                    bg = "blue"
                else:
                    fg = "white"
                    bg = "green"
                self.draw_tile(
                    x * 2 + i * (self.tile_width + self.offset_x),
                    j * (self.tile_height + self.offset_y),
                    text=PIECES[0],
                    fg=fg,
                    bg=bg,
                )
        for i in range(len(self)):
            with self.term.location(
                x * 2 + i * self.tile_width, len(self) * self.tile_height
            ):
                print(str.center(ROW[i], len(self)))
        print(self.term.move_y(self.term.height - 4))
        print(self.term.black_on_blue(self.term.center("press the move")))

    def start_game(self) -> int:
        """Starts the chess game."""
        pass


game = Game()
game.show_game_screen()
