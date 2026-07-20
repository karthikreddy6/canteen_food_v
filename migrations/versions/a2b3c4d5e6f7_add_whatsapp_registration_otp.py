"""add WhatsApp registration OTP"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "a2b3c4d5e6f7"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("phone_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    # Existing accounts predate WhatsApp verification and must keep working.
    op.execute("UPDATE users SET phone_verified = true")
    op.create_table(
        "registration_otps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_registration_otps_user_id", "registration_otps", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_registration_otps_user_id", table_name="registration_otps")
    op.drop_table("registration_otps")
    op.drop_column("users", "phone_verified")
