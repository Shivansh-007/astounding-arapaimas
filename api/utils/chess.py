import logging

import Chessnut
from Chessnut import Game

from api.crud import game
from api.endpoints import get_db

logger = logging.getLogger(__name__)


class ChessBoard:
    """Base class for chess board game."""

    def __init__(self, fen: str, game_id: int):
        self.FEN = fen  # will be given by server when multiplayer is added
        self.board = Game(self.FEN)
        self.game_id = game_id
        self.db = next(get_db())

    def give_board(self) -> str:
        """Returns the board in FEN representation."""
        return game.get_board_by_id(self.db, game_id=self.game_id)

    def all_available_moves(self) -> list:
        """Returns all moves that each piece of a player can make."""
        return self.board.get_moves()

    def move_piece(self, move: str) -> None:
        """Function to apply a move defined in simple algebraic notation like a1b1."""
        self.board.apply_move(move)

        game.update_board_by_id(
            self.db, game_id=self.game_id, board=self.board.get_fen()
        )

    def reset(self) -> None:
        """Reset the board to initial position."""
        self.board.reset()

        game.update_board_by_id(
            self.db, game_id=self.game_id, board=self.board.get_fen()
        )
        logger.info("Resetting the Board")
