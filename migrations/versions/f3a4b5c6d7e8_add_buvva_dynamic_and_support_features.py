"""add buvva dynamic and support features

Revision ID: f3a4b5c6d7e8
Revises: f2a3b4c5d6e7
Create Date: 2026-10-04 03:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'f3a4b5c6d7e8'
down_revision: Union[str, Sequence[str], None] = 'f2a3b4c5d6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users: avatar & gender
    op.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS avatar VARCHAR(50) DEFAULT 'default',
        ADD COLUMN IF NOT EXISTS gender VARCHAR(20) DEFAULT NULL;
    """)

    # 2. colleges: photo_url, map_url, latitude, longitude
    op.execute("""
        ALTER TABLE colleges
        ADD COLUMN IF NOT EXISTS photo_url TEXT DEFAULT NULL,
        ADD COLUMN IF NOT EXISTS map_url TEXT DEFAULT NULL,
        ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION DEFAULT NULL,
        ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION DEFAULT NULL;
    """)

    # 3. canteens: photo_url, map_url, location_description, latitude, longitude
    op.execute("""
        ALTER TABLE canteens
        ADD COLUMN IF NOT EXISTS photo_url TEXT DEFAULT NULL,
        ADD COLUMN IF NOT EXISTS map_url TEXT DEFAULT NULL,
        ADD COLUMN IF NOT EXISTS location_description TEXT DEFAULT NULL,
        ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION DEFAULT NULL,
        ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION DEFAULT NULL;
    """)

    # 4. support_tickets: CLOSED enum, order_id & updated_at
    op.execute("""
        ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'CLOSED';
    """)
    op.execute("""
        ALTER TABLE support_tickets
        ADD COLUMN IF NOT EXISTS order_id UUID DEFAULT NULL REFERENCES orders(id) ON DELETE SET NULL,
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    """)

    # 5. support_messages table
    op.execute("""
        CREATE TABLE IF NOT EXISTS support_messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            ticket_id UUID NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
            sender_type VARCHAR(20) NOT NULL,
            sender_id VARCHAR(64) NOT NULL,
            sender_name VARCHAR(100) DEFAULT 'Support',
            message TEXT NOT NULL,
            channel VARCHAR(20) DEFAULT 'APP',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # 6. Index on support_messages.ticket_id
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_support_messages_ticket ON support_messages(ticket_id);
    """)

    # 7. PostgreSQL trigger for real-time support message broadcast
    op.execute("""
        CREATE OR REPLACE FUNCTION notify_support_message() RETURNS trigger AS $trg$
        DECLARE
            ticket_user_id text;
            notification json;
        BEGIN
            SELECT user_id INTO ticket_user_id FROM support_tickets WHERE id = NEW.ticket_id;
            notification = json_build_object(
                'type', 'chat_message',
                'messageId', NEW.id::text,
                'ticketId', NEW.ticket_id::text,
                'userId', ticket_user_id,
                'senderType', NEW.sender_type,
                'senderName', NEW.sender_name,
                'message', NEW.message,
                'channel', NEW.channel,
                'timestamp', NEW.created_at
            );
            PERFORM pg_notify('onfood_events', json_build_object('event', 'support_message_created', 'data', notification)::text);
            RETURN NEW;
        END;
        $trg$ LANGUAGE plpgsql;
    """)
    op.execute("DROP TRIGGER IF EXISTS trg_support_message_notify ON support_messages;")
    op.execute("""
        CREATE TRIGGER trg_support_message_notify
        AFTER INSERT ON support_messages
        FOR EACH ROW EXECUTE FUNCTION notify_support_message();
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS support_messages CASCADE;")
    op.execute("ALTER TABLE support_tickets DROP COLUMN IF EXISTS updated_at;")
    op.execute("ALTER TABLE support_tickets DROP COLUMN IF EXISTS order_id;")
    op.execute("ALTER TABLE canteens DROP COLUMN IF EXISTS longitude, DROP COLUMN IF EXISTS latitude, DROP COLUMN IF EXISTS location_description, DROP COLUMN IF EXISTS map_url, DROP COLUMN IF EXISTS photo_url;")
    op.execute("ALTER TABLE colleges DROP COLUMN IF EXISTS longitude, DROP COLUMN IF EXISTS latitude, DROP COLUMN IF EXISTS map_url, DROP COLUMN IF EXISTS photo_url;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS gender, DROP COLUMN IF EXISTS avatar;")
