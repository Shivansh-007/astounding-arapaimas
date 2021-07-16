from app import ascii_art

GAME_WELCOME_BOTTOM = (
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
GAME_WELCOME_TOP = (
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

MENU_MAPPING = {
    " Create Game ": (
        "Creates an new game and waits for an opponent to join",
        "gm_options",
        "gm_options_highlight",
    ),
    " Join Game ": (
        "Join a pre-existing game of your choice",
        "gm_options",
        "gm_options_highlight",
    ),
    " Settings ": ("Change game settings", "gm_options", "gm_options_highlight"),
    " Exit ": ("Exit the game", "gm_exit", "gm_exit_highlight"),
}

CHESS_STATUS = {"NORMAL": 0, "CHECK": 1, "CHECKMATE": 2, "STALEMATE": 3}

PIECES = "".join(chr(9812 + x) for x in range(12))

COL = ("A", "B", "C", "D", "E", "F", "G", "H")

ROW = tuple(map(str, range(1, 9)))

INITIAL_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

POSSIBLE_CASTLING_MOVES = ("e1g1", "e8g8", "e1c1", "e8c8")

BLACK_PIECES = ("r", "n", "b", "q", "k", "p")

WHITE_PIECES = ("R", "N", "B", "Q", "K", "P")
