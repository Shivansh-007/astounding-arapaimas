from typing import Optional

import Chessnut
from Chessnut import Game


class ChessBoard:
    """default class for chess board game."""

    def __init__(self, fen: str):
        self.FEN = fen  # will be given by server when multiplayer is added
        self.board = Game(self.FEN)

    def give_board(self) -> str:
        """returns the board in."""
        return self.board.get_fen()

    def all_available_moves(self) -> list:
        return self.board.get_moves()

    def move_piece(self, move: str) -> Optional[int]:
        """function to apply a move defined in simple algebraic notation like a1b1."""
        try:
            self.board.apply_move(move)
        except Chessnut.game.InvalidMove:
            return -1

    def reset(self):
        """reset the board to initial position."""
        self.board.reset()
