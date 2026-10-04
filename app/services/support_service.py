"""
Support Service Client for OnFood Backend
Connects onfoodserver (FastAPI) to onfood-whatsapp-bot (Support Desk & WhatsApp Engine) via HTTP.
Contract defined in SUPPORT_DESK_COMMUNICATION_GUIDE.md.
"""
import os
import logging
from typing import Optional, Dict, Any
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


def _get_support_bot_url() -> str:
    url = (
        os.getenv("SUPPORT_BOT_URL")
        or getattr(settings, "SUPPORT_BOT_URL", None)
        or os.getenv("WHATSAPP_BOT_URL")
        or getattr(settings, "WHATSAPP_BOT_URL", None)
        or "http://127.0.0.1:3000"
    )
    return url.rstrip("/")


def _get_internal_api_key() -> str:
    return (
        os.getenv("INTERNAL_API_KEY")
        or getattr(settings, "INTERNAL_API_KEY", None)
        or os.getenv("WHATSAPP_BOT_INTERNAL_KEY")
        or getattr(settings, "WHATSAPP_BOT_INTERNAL_KEY", None)
        or ""
    )


class SupportServiceClient:
    def __init__(self, base_url: Optional[str] = None):
        self._custom_base_url = base_url

    @property
    def base_url(self) -> str:
        return (self._custom_base_url or _get_support_bot_url()).rstrip("/")

    @property
    def internal_key(self) -> str:
        return _get_internal_api_key()

    async def send_delay_alert(
        self,
        order_id: str,
        buffer_minutes: int = 10,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Notify support desk and customer of order delay."""
        url = f"{self.base_url}/api/orders/{order_id}/delay-alert"
        payload = {"minutes": buffer_minutes}
        if custom_message:
            payload["message"] = custom_message

        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                res = await client.post(url, json=payload)
                res.raise_for_status()
                return res.json()
        except Exception as exc:
            logger.warning("Failed to notify support desk of delay on order %s: %s", order_id, exc)
            return {"ok": False, "error": str(exc)}

    async def send_whatsapp_otp(
        self,
        phone: str,
        otp_code: str,
        expires_minutes: int = 5
    ) -> bool:
        """Send verification OTP code via WhatsApp."""
        url = f"{self.base_url}/internal/whatsapp/send-otp"
        headers = {"x-internal-api-key": self.internal_key}
        payload = {
            "phone": phone,
            "otp": str(otp_code),
            "expiresInMinutes": expires_minutes
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                return res.status_code == 200
        except Exception as exc:
            logger.warning("Failed to send WhatsApp OTP to %s: %s", phone, exc)
            return False

    async def send_customer_message(
        self,
        phone: str,
        message: str,
        channel: str = "BOTH"  # 'WHATSAPP' | 'APP' | 'BOTH'
    ) -> Dict[str, Any]:
        """Send message to customer via chosen channel."""
        url = f"{self.base_url}/api/messages/send"
        payload = {
            "phone": phone,
            "message": message,
            "channel": channel.upper()
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload)
                return res.json()
        except Exception as exc:
            logger.warning("Failed to send customer message to %s: %s", phone, exc)
            return {"ok": False, "error": str(exc)}

    async def create_support_ticket(
        self,
        user_phone: str,
        category: str,
        description: str,
        order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Forward support ticket creation to Support Desk."""
        url = f"{self.base_url}/api/tickets/create"
        payload = {
            "userPhone": user_phone,
            "category": category,
            "description": description,
        }
        if order_id:
            payload["orderId"] = str(order_id)

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload)
                return res.json()
        except Exception as exc:
            logger.warning("Failed to forward ticket creation to support desk: %s", exc)
            return {"ok": False, "error": str(exc)}


# Global client singleton instance
support_client = SupportServiceClient()
support_service = support_client
