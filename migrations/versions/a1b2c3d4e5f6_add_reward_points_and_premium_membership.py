"""add_reward_points_and_premium_membership

Revision ID: a1b2c3d4e5f6
Revises: 9639d26777df
Create Date: 2026-08-24 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '9639d26777df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add reward points, premium membership, and brand coupons."""

    # 1. Create points_transaction_type enum safely
    op.execute(
        "DO $$ BEGIN "
        "CREATE TYPE points_transaction_type AS ENUM ('EARNED', 'REDEEMED', 'BONUS', 'REFUNDED'); "
        "EXCEPTION WHEN duplicate_object THEN null; "
        "END $$;"
    )

    # 2. Add reward & premium columns to users
    op.add_column('users', sa.Column('reward_points_balance', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('lifetime_points_earned', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('is_premium', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('premium_expires_at', sa.DateTime(), nullable=True))

    # 3. Add points_earned to orders
    op.add_column('orders', sa.Column('points_earned', sa.Integer(), nullable=False, server_default='0'))

    # 4. Create points_transactions table
    op.create_table(
        'points_transactions',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('order_id', UUID(as_uuid=True), nullable=True),
        sa.Column('type', postgresql.ENUM('EARNED', 'REDEEMED', 'BONUS', 'REFUNDED', name='points_transaction_type', create_type=False), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('balance_after', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_points_transactions_user_id', 'points_transactions', ['user_id'])

    # 5. Create brand_coupons table
    op.create_table(
        'brand_coupons',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('brand_name', sa.String(), nullable=False),
        sa.Column('brand_logo_url', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('coupon_code', sa.String(), nullable=False),
        sa.Column('points_cost', sa.Integer(), nullable=False),
        sa.Column('is_claimed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('claimed_by', sa.String(), nullable=True),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['claimed_by'], ['users.id'], ondelete='SET NULL'),
    )


def downgrade() -> None:
    """Remove reward points, premium membership, and brand coupons."""

    op.drop_table('brand_coupons')

    op.drop_index('ix_points_transactions_user_id', table_name='points_transactions')
    op.drop_table('points_transactions')

    op.drop_column('orders', 'points_earned')

    op.drop_column('users', 'premium_expires_at')
    op.drop_column('users', 'is_premium')
    op.drop_column('users', 'lifetime_points_earned')
    op.drop_column('users', 'reward_points_balance')

    sa.Enum(name='points_transaction_type').drop(op.get_bind(), checkfirst=True)
