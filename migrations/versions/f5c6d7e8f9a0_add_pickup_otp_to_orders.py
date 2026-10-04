"""add pickup_otp to orders

Revision ID: f5c6d7e8f9a0
Revises: f4b5c6d7e8f9
Create Date: 2026-10-04 08:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'f5c6d7e8f9a0'
down_revision: Union[str, Sequence[str], None] = 'f4b5c6d7e8f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE orders 
        ADD COLUMN IF NOT EXISTS pickup_otp VARCHAR(10) DEFAULT NULL;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE orders 
        DROP COLUMN IF EXISTS pickup_otp;
    """)
