import os
import time
import asyncio
import logging
from typing import List, Dict, Any, Optional

import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserFcmToken
from app.config import settings

logger = logging.getLogger("onfood.fcm")


def _init_firebase_app():
    """Initializes Firebase Admin SDK if credentials file exists and not yet initialized."""
    try:
        cred_path = getattr(settings, "FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
        if os.path.exists(cred_path) and not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info(f"[FCM] Firebase Admin SDK initialized successfully from '{cred_path}'")
        elif not os.path.exists(cred_path):
            logger.warning(f"[FCM] Firebase credentials not found at '{cred_path}'. Push notifications disabled.")
    except Exception as e:
        logger.error(f"[FCM] Failed to initialize Firebase Admin SDK: {e}")


# Initialize once on module load
_init_firebase_app()


def _build_status_copy(status: str, token_display: str) -> tuple[str, str]:
    """Return friendly (title, message) for each order status."""
    st = (status or "").upper().strip()
    if st == "PREPARING":
        return "Kitchen is Cooking 🍳", f"Token #{token_display} is being prepared by the chef!"
    elif st in ("READY", "READY_FOR_PICKUP"):
        return "Order Ready to Collect! 🔔", f"Token #{token_display} is ready at the counter!"
    elif st in ("DELIVERED", "CLOSED"):
        return "Order Collected ✅", f"Enjoy your meal! Token #{token_display} completed."
    elif st in ("CANCELLED", "REJECTED", "FAILED"):
        return "Order Cancelled", f"Order #{token_display} has been cancelled."
    return "Order Update", f"Your order status is now: {status}"


def _dispatch_multicast_sync(tokens: List[str], data_payload: Dict[str, str]) -> List[str]:
    """
    Synchronous worker executed in threadpool to send FCM multicast
    and collect stale tokens for pruning.
    """
    stale_tokens: List[str] = []
    try:
        message = messaging.MulticastMessage(
            tokens=tokens,
            data=data_payload,
            android=messaging.AndroidConfig(
                priority="high",
                ttl=86400  # 24 hours in seconds
            )
        )
        response = messaging.send_each_for_multicast(message)
        logger.info(
            f"[FCM] Sent {response.success_count}/{len(tokens)} push messages for order {data_payload.get('order_id')}"
        )

        if response.failure_count > 0:
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    err_code = getattr(resp.exception, "code", "")
                    err_msg = str(resp.exception)
                    if (
                        "registration-token-not-registered" in str(err_code)
                        or "invalid-registration-token" in str(err_code)
                        or "UnregisteredError" in err_msg
                    ):
                        stale_tokens.append(tokens[idx])
    except Exception as e:
        logger.error(f"[FCM] Failed to dispatch multicast push: {e}")

    return stale_tokens


async def send_order_status_push_async(
    db: AsyncSession,
    user_id: str,
    order_id: str,
    order_token: str,
    status: str,
    estimated_ready_at: Optional[str] = None,
    items_details: Optional[str] = None
):
    """
    Queries active FCM tokens for the given user_id and dispatches a high-priority
    DATA-ONLY FCM message. Runs on a threadpool to prevent blocking the async event loop.
    """
    if not firebase_admin._apps:
        return

    # 1. Fetch user's registered FCM tokens
    stmt = select(UserFcmToken.fcm_token).where(UserFcmToken.user_id == user_id)
    result = await db.execute(stmt)
    tokens: List[str] = result.scalars().all()

    if not tokens:
        logger.debug(f"[FCM] No registered device tokens for user_id={user_id}")
        return

    title, message = _build_status_copy(status, order_token or "")

    # 2. Build High-Priority DATA payload (PURE DATA ONLY - no top-level 'notification' block!)
    data_payload = {
        "type": "ORDER_STATUS_UPDATE",
        "order_id": str(order_id),
        "order_token": str(order_token or ""),
        "status": str(status).upper(),
        "estimated_ready_at": str(estimated_ready_at or ""),
        "items_details": str(items_details or "Food tray items"),
        "title": title,
        "message": message,
        "timestamp": str(int(time.time() * 1000)),
    }

    # 3. Dispatch using send_each_for_multicast in threadpool
    loop = asyncio.get_running_loop()
    stale_tokens = await loop.run_in_executor(None, _dispatch_multicast_sync, tokens, data_payload)

    # 4. Prune stale tokens from database and Cloud Firestore
    if stale_tokens:
        logger.info(f"[FCM] Pruning {len(stale_tokens)} stale token(s) from database and Firestore")
        try:
            delete_stmt = delete(UserFcmToken).where(UserFcmToken.fcm_token.in_(stale_tokens))
            await db.execute(delete_stmt)
            await db.commit()
        except Exception as e:
            logger.error(f"[FCM] Failed to prune stale tokens from DB: {e}")

        try:
            from app.services.firestore_sync import prune_tokens_from_firestore
            await prune_tokens_from_firestore(user_id=user_id, tokens=stale_tokens)
        except Exception as e:
            logger.warning(f"[Firestore] Failed to prune stale tokens from Firestore: {e}")

