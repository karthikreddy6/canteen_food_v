"""add payment_method and order_confirmation_otps

Revision ID: f6c7d8e9f0a1
Revises: f5c6d7e8f9a0
Create Date: 2026-10-04 08:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'f6c7d8e9f0a1'
down_revision: Union[str, Sequence[str], None] = 'f5c6d7e8f9a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE orders 
        ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50) NOT NULL DEFAULT 'PAY_AT_COUNTER';
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS order_confirmation_otps (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            code_hash VARCHAR NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_order_confirmation_otps_user_id UNIQUE (user_id)
        );
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_order_confirmation_otps_user_id ON order_confirmation_otps(user_id);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS order_confirmation_otps;")
    op.execute("""
        ALTER TABLE orders 
        DROP COLUMN IF EXISTS payment_method;
    """)
