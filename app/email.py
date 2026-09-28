"""
Zoho SMTP email utility for the OnFood backend.

Usage:
    from app.email import send_email

    # Simple text email
    await send_email(
        to="user@example.com",
        subject="Order Confirmed",
        body="Your order #123 has been placed!",
    )

    # HTML email
    await send_email(
        to="user@example.com",
        subject="Order Confirmed",
        body="<h1>Order Confirmed!</h1><p>Your order #123 is being prepared.</p>",
        html=True,
    )
"""

import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings

_logger = logging.getLogger("onfood.email")


def _send_email_sync(
    to: str,
    subject: str,
    body: str,
    html: bool = False,
) -> bool:
    """
    Synchronous SMTP send (called via asyncio.to_thread to avoid blocking the event loop).
    Returns True on success, False on failure.
    """
    if not settings.SMTP_EMAIL or not settings.SMTP_PASSWORD:
        _logger.warning("[EMAIL] SMTP_EMAIL or SMTP_PASSWORD not configured — email not sent.")
        return False

    msg = MIMEMultipart()
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_EMAIL}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html" if html else "plain", "utf-8"))

    server = None
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        server.starttls()
        server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_EMAIL, to, msg.as_string())
        _logger.info(f"[EMAIL] Sent to {to}: {subject}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        _logger.error(f"[EMAIL] SMTP authentication failed: {e}")
        return False
    except smtplib.SMTPException as e:
        _logger.error(f"[EMAIL] SMTP error sending to {to}: {e}")
        return False
    except Exception as e:
        _logger.error(f"[EMAIL] Unexpected error sending to {to}: {e}")
        return False
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass


async def send_email(
    to: str,
    subject: str,
    body: str,
    html: bool = False,
) -> bool:
    """
    Send an email asynchronously via Zoho SMTP.
    Runs the blocking SMTP call in a thread pool so the event loop is not blocked.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body (plain text or HTML).
        html: If True, body is treated as HTML.

    Returns:
        True if the email was sent successfully, False otherwise.
    """
    return await asyncio.to_thread(_send_email_sync, to, subject, body, html)
