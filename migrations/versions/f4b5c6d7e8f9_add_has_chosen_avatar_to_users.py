"""add has_chosen_avatar to users

Revision ID: f4b5c6d7e8f9
Revises: f3a4b5c6d7e8
Create Date: 2026-10-04 07:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'f4b5c6d7e8f9'
down_revision: Union[str, Sequence[str], None] = 'f3a4b5c6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS has_chosen_avatar BOOLEAN NOT NULL DEFAULT FALSE;
    """)
    op.execute("""
        UPDATE users 
        SET has_chosen_avatar = TRUE 
        WHERE (avatar IS NOT NULL AND avatar != 'default') OR gender IS NOT NULL;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE users 
        DROP COLUMN IF EXISTS has_chosen_avatar;
    """)
