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
        "bold_white_on_green",
    ),
    " Join Game ": ("Join a pre-existing game of your choice", "bold_white_on_green"),
    " Settings ": ("Change game settings", "bold_white_on_green"),
    " Exit ": ("Exit the game", "bold_white_on_red"),
}
