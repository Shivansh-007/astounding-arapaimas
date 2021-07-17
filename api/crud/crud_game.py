import typing as t

from sqlalchemy.orm import Session

from api.crud.base import CRUDBase
from api.models import Game
from api.schemas.game import GameCreate, GameUpdate


class CRUDGame(CRUDBase[Game, GameCreate, GameUpdate]):
    """View providing CRUD operations on authenticated users."""

    def get_by_game_id(self, db: Session, *, game_id: int) -> t.Optional[Game]:
        """Get a game model object by game_id."""
        return db.query(Game).filter(Game.game_id == game_id).first()

    def get_board_by_id(self, db: Session, *, game_id: int) -> t.Optional[str]:
        """Get the board of the game with id `game_id`."""
        game_obj = self.get_by_game_id(db, game_id=game_id)
        if not game_obj:
            return None

        return game_obj.board

    def get_open_games(self, db: Session) -> list[int]:
        """Get IDs of all games which have no player 2 set i.e. haven't started yet."""
        return db.query(Game).filter(Game.player_two_id == 0).all()

    def player_already_in_game(self, db: Session, *, user_id: int) -> bool:
        """Returns whether the user is already in a game or not."""
        user_open_games = (
            db.query(Game)
            .filter(Game.player_one_id == user_id)
            .filter(Game.is_ongoing is False)
            .all()
        )
        return len(user_open_games) > 0

    def update_board_by_id(
        self, db: Session, *, game_id: int, board: str
    ) -> t.Optional[Game]:
        """Update the board of the game with id `game_id`."""
        game_obj = self.get_by_game_id(db, game_id=game_id)
        if not game_obj:
            return None

        game_obj.board = board
        db.add(game_obj)
        db.commit()
        db.refresh(game_obj)
        return game_obj

    def create(self, db: Session, *, obj_in: GameCreate) -> Game:
        """Make a new game object, and add it to the database."""
        db_obj = Game(
            game_id=obj_in.game_id,
            winner_id=obj_in.winner_id,
            player_one_id=obj_in.player_one_id,
            player_two_id=obj_in.player_two_id,
            is_ongoing=obj_in.is_ongoing,
            board=obj_in.board,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def set_player_two(
        self, db: Session, *, game_id: int, player_id: int
    ) -> t.Union[str, Game]:
        """Sets the second player ID for the game after validating it."""
        game_obj = self.get_by_game_id(db, game_id=game_id)

        if game_obj.player_two_id:
            return "Game has already started with another user."

        game_obj.player_two_id = player_id
        db.add(game_obj)
        db.commit()
        db.refresh(game_obj)
        return game_obj

    def mark_game_winner(
        self, db: Session, *, game_id: int, winner_id: int
    ) -> t.Optional[Game]:
        """
        Mark the game complete and set the winner_id.

        Before setting the winner_id, the function first checks if the winner_id exists
        as player two or one ID or not. If it doesn't it returns None else it sets it.
        """
        game_obj = self.get_by_game_id(db, game_id=game_id)
        if not game_obj:
            return None

        if winner_id not in (game_obj.player_one_id, game_obj.player_two_id):
            return None

        game_obj.winner_id = winner_id
        game_obj.is_ongoing = False
        db.add(game_obj)
        db.commit()
        db.refresh(game_obj)
        return game_obj

    def get_player_count(self, db: Session, *, game_id: int) -> int:
        """Returns the number of players in a room."""
        len_players = 0
        game_obj = self.get_by_game_id(db, game_id=game_id)
        if game_obj.player_one_id:
            len_players += 1
        if game_obj.player_two_id:
            len_players += 1
        return len_players


game = CRUDGame(Game)
