"""add configurable order token"""

from alembic import op
import sqlalchemy as sa

revision = "c1d8e4f09a22"
down_revision = "b7c4e1a2d903"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("order_token", sa.String(), nullable=True))
    op.create_index("ix_orders_order_token", "orders", ["order_token"], unique=False)
    op.add_column(
        "kitchen_settings",
        sa.Column("use_roll_number_as_order_token", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("kitchen_settings", "use_roll_number_as_order_token")
    op.drop_index("ix_orders_order_token", table_name="orders")
    op.drop_column("orders", "order_token")
