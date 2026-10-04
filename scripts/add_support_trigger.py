import asyncio
from sqlalchemy import text
from app.database import engine

statements = [
    """
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
    """,
    "DROP TRIGGER IF EXISTS trg_support_message_notify ON support_messages;",
    """
    CREATE TRIGGER trg_support_message_notify
    AFTER INSERT ON support_messages
    FOR EACH ROW EXECUTE FUNCTION notify_support_message();
    """
]

async def run():
    async with engine.begin() as conn:
        for stmt in statements:
            await conn.execute(text(stmt))
    print("Trigger created successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run())
