"""Add user model

Revision ID: a4bfab0f7c83
Revises:
Create Date: 2021-07-12 06:55:12.069575

"""
from alembic import op
import sqlalchemy


# revision identifiers, used by Alembic.
revision = "a4bfab0f7c83"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user",
        sqlalchemy.Column(
            "user_id", sqlalchemy.BigInteger, primary_key=True, unique=True
        ),
        sqlalchemy.Column("token_salt", sqlalchemy.String),
        sqlalchemy.Column("is_staff", sqlalchemy.Boolean),
        sqlalchemy.Column("is_banned", sqlalchemy.Boolean),
    )


def downgrade() -> None:
    op.drop_table("user")
