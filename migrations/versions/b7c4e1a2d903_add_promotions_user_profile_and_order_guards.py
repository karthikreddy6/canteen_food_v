"""add promotions, user campus profile, and order guard fields"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "b7c4e1a2d903"
down_revision = "9b4e7f2a1c11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("roll_number", sa.String(), nullable=True))
    op.add_column("users", sa.Column("campus", sa.String(), nullable=True))
    op.add_column("users", sa.Column("college", sa.String(), nullable=True))
    op.add_column("users", sa.Column("last_order_at", sa.DateTime(), nullable=True))
    op.create_index("ix_users_roll_number", "users", ["roll_number"], unique=True)
    op.add_column("orders", sa.Column("user_roll_number", sa.String(), nullable=True))
    op.add_column("orders", sa.Column("discount_amount", sa.Numeric(10, 2), nullable=False, server_default="0"))
    op.add_column("orders", sa.Column("coupon_code", sa.String(), nullable=True))
    op.create_index("ix_orders_user_roll_number", "orders", ["user_roll_number"], unique=False)
    op.create_table(
        "coupons",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("discount_type", sa.String(), nullable=False, server_default="PERCENT"),
        sa.Column("value", sa.Numeric(10, 2), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("max_uses", sa.Integer(), nullable=True),
        sa.Column("used_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("code"),
    )
    op.create_index("ix_coupons_code", "coupons", ["code"], unique=True)
    op.create_table(
        "banners",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("link_url", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("starts_at", sa.DateTime(), nullable=True),
        sa.Column("ends_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("banners")
    op.drop_index("ix_coupons_code", table_name="coupons")
    op.drop_table("coupons")
    op.drop_index("ix_orders_user_roll_number", table_name="orders")
    op.drop_column("orders", "coupon_code")
    op.drop_column("orders", "discount_amount")
    op.drop_column("orders", "user_roll_number")
    op.drop_index("ix_users_roll_number", table_name="users")
    op.drop_column("users", "last_order_at")
    op.drop_column("users", "college")
    op.drop_column("users", "campus")
    op.drop_column("users", "roll_number")
