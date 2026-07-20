"""add per-user order token preference"""

from alembic import op
import sqlalchemy as sa

revision = "d4f6a1b8c203"
down_revision = "c1d8e4f09a22"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("use_roll_number_as_order_token", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("users", "use_roll_number_as_order_token")
