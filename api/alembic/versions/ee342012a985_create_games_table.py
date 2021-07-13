"""Create games table

Revision ID: ee342012a985
Revises: a4bfab0f7c83
Create Date: 2021-07-13 06:32:32.456387

"""
from alembic import op
import sqlalchemy


# revision identifiers, used by Alembic.
revision = "ee342012a985"
down_revision = "a4bfab0f7c83"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "game",
        sqlalchemy.Column(
            "game_id", sqlalchemy.BigInteger, primary_key=True, unique=True
        ),
        sqlalchemy.Column("is_ongoing", sqlalchemy.Boolean, default=True),
        sqlalchemy.Column("winner_id", sqlalchemy.BigInteger),
        sqlalchemy.Column("player_one_id", sqlalchemy.BigInteger),
        sqlalchemy.Column("player_two_id", sqlalchemy.BigInteger),
    )


def downgrade() -> None:
    op.drop_table("game")
