"""restore orders table after accidental drop

The database was marked at the latest Alembic revision even though the
orders table was removed manually.  This migration recreates the table in
the shape used by app.models.Order and restores the five order rows that
were recorded in the server SQL log.  Existing order_items are intentionally
left untouched because some of them no longer have recoverable parent rows.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import datetime as dt


revision = "e8a7c6d5b4f3"
down_revision = "d4f6a1b8c203"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("user_roll_number", sa.String(), nullable=True),
        sa.Column("order_token", sa.String(), nullable=True),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("coupon_code", sa.String(), nullable=True),
        sa.Column("status", postgresql.ENUM(name="order_status", create_type=False), nullable=False),
        sa.Column("pickup_number", sa.Integer(), nullable=True),
        sa.Column("pickup_date", sa.Date(), nullable=True),
        sa.Column("estimated_ready_at", sa.DateTime(), nullable=True),
        sa.Column("actual_ready_at", sa.DateTime(), nullable=True),
        sa.Column("scheduled_date", sa.Date(), nullable=True),
        sa.Column("scheduled_slot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["scheduled_slot_id"], ["time_slots.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_user_roll_number", "orders", ["user_roll_number"])
    op.create_index("ix_orders_order_token", "orders", ["order_token"])

    # Reinsert rows whose complete values are available in server.uvicorn...log.
    orders = sa.table(
        "orders",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("user_id", sa.String()),
        sa.column("total_amount", sa.Numeric(10, 2)),
        sa.column("status", postgresql.ENUM(name="order_status", create_type=False)),
        sa.column("pickup_number", sa.Integer()),
        sa.column("pickup_date", sa.Date()),
        sa.column("estimated_ready_at", sa.DateTime()),
        sa.column("scheduled_date", sa.Date()),
        sa.column("scheduled_slot_id", postgresql.UUID(as_uuid=True)),
        sa.column("notes", sa.String()),
        sa.column("created_at", sa.DateTime()),
    )
    op.bulk_insert(orders, [
        {"id": "8feb0293-7b9c-40b6-b219-5a3c2d680620", "user_id": "210ef85c-98a8-40cc-9add-c26e261ab2b2", "total_amount": 249, "status": "SCHEDULED", "pickup_number": 1, "pickup_date": dt.date(2026, 7, 13), "estimated_ready_at": dt.datetime(2026, 7, 13, 12, 30), "scheduled_date": dt.date(2026, 7, 13), "scheduled_slot_id": "100c7e31-658d-44ce-b3d1-c99383db12e6", "notes": "Scheduled order #1 via powershell test", "created_at": dt.datetime(2026, 7, 12, 18, 30, 2, 600633)},
        {"id": "b6459af1-6ab6-4042-be0c-857f708d1ff6", "user_id": "210ef85c-98a8-40cc-9add-c26e261ab2b2", "total_amount": 269, "status": "SCHEDULED", "pickup_number": 2, "pickup_date": dt.date(2026, 7, 13), "estimated_ready_at": dt.datetime(2026, 7, 13, 15, 30), "scheduled_date": dt.date(2026, 7, 13), "scheduled_slot_id": "5ffd75b5-3fe2-4a48-806c-f2809a075539", "notes": "Scheduled order #2 via powershell test", "created_at": dt.datetime(2026, 7, 12, 18, 30, 2, 938754)},
        {"id": "d4328ce9-11ba-4d96-8df9-f46ba1893bdc", "user_id": "210ef85c-98a8-40cc-9add-c26e261ab2b2", "total_amount": 349, "status": "SCHEDULED", "pickup_number": 3, "pickup_date": dt.date(2026, 7, 13), "estimated_ready_at": dt.datetime(2026, 7, 13, 18, 30), "scheduled_date": dt.date(2026, 7, 13), "scheduled_slot_id": "4475757a-2e73-4d2e-bd92-fe6b334d3e20", "notes": "Scheduled order #3 via powershell test", "created_at": dt.datetime(2026, 7, 12, 18, 30, 3, 240492)},
        {"id": "c8b81604-b075-46c4-b0f7-f40676290241", "user_id": "210ef85c-98a8-40cc-9add-c26e261ab2b2", "total_amount": 179, "status": "SCHEDULED", "pickup_number": 4, "pickup_date": dt.date(2026, 7, 13), "estimated_ready_at": dt.datetime(2026, 7, 14, 13, 30), "scheduled_date": dt.date(2026, 7, 14), "scheduled_slot_id": "9a60642e-edf1-4e8f-a070-89f4a5b443cf", "notes": "Scheduled order #4 via powershell test", "created_at": dt.datetime(2026, 7, 12, 18, 30, 3, 547351)},
        {"id": "4fa5d875-ffb5-4a6c-b16e-c48712463f29", "user_id": "210ef85c-98a8-40cc-9add-c26e261ab2b2", "total_amount": 99, "status": "SCHEDULED", "pickup_number": 5, "pickup_date": dt.date(2026, 7, 13), "estimated_ready_at": dt.datetime(2026, 7, 14, 19, 30), "scheduled_date": dt.date(2026, 7, 14), "scheduled_slot_id": "e3adf1c0-f2f9-4121-8437-11d7a1c131c5", "notes": "Scheduled order #5 via powershell test", "created_at": dt.datetime(2026, 7, 12, 18, 30, 3, 851527)},
    ])


def downgrade() -> None:
    op.drop_index("ix_orders_order_token", table_name="orders")
    op.drop_index("ix_orders_user_roll_number", table_name="orders")
    op.drop_table("orders")
