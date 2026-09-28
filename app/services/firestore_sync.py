import asyncio
import datetime
import logging
from typing import List, Optional

from app.config import settings

logger = logging.getLogger("onfood.firestore")

_mongo_client = None


def _get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        mongo_uri = getattr(settings, "FIRESTORE_MONGO_URI", None)
        if mongo_uri:
            try:
                import pymongo
                _mongo_client = pymongo.MongoClient(
                    mongo_uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=5000,
                )
                logger.info("[Firestore] Initialized MongoDB API client successfully.")
            except Exception as e:
                logger.error(f"[Firestore] Failed to initialize MongoDB client: {e}")
                _mongo_client = None
    return _mongo_client


def _get_db(client):
    try:
        db = client.get_default_database()
        if db is not None:
            return db
    except Exception:
        pass
    return client["default"]


def _sync_token_sync(user_id: str, token: str, device_name: str, platform: str) -> None:
    now_iso = datetime.datetime.utcnow().isoformat()
    device_key = token.replace(".", "_")[-24:]

    # 1. Sync via MongoDB API (Firestore MongoDB Mode)
    client = _get_mongo_client()
    if client is not None:
        try:
            db = _get_db(client)
            db.users.update_one(
                {"userId": user_id},
                {
                    "$set": {
                        "userId": user_id,
                        "lastActive": now_iso,
                        f"devices.{device_key}": {
                            "token": token,
                            "deviceName": device_name,
                            "platform": platform,
                            "updatedAt": now_iso,
                        },
                    },
                    "$addToSet": {"fcmTokens": token},
                },
                upsert=True,
            )
            logger.info(f"[Firestore-Mongo] Synced token for user_id={user_id} ({device_name})")
        except Exception as e:
            logger.warning(f"[Firestore-Mongo] Error syncing token: {e}")

    # 2. Sync via Native Firebase Admin (Firestore Native Mode)
    try:
        import firebase_admin
        if firebase_admin._apps:
            from firebase_admin import firestore
            fs = firestore.client()
            user_ref = fs.collection("users").document(user_id)
            user_ref.set({
                "userId": user_id,
                "fcmTokens": firestore.ArrayUnion([token]),
                "lastActive": firestore.SERVER_TIMESTAMP,
                "devices": {
                    device_key: {
                        "token": token,
                        "deviceName": device_name,
                        "platform": platform,
                        "updatedAt": firestore.SERVER_TIMESTAMP,
                    }
                }
            }, merge=True)
            logger.info(f"[Firestore-Native] Synced token for user_id={user_id}")
    except Exception as e:
        logger.debug(f"[Firestore-Native] Native sync bypassed: {e}")


def _remove_token_sync(user_id: str, token: str) -> None:
    device_key = token.replace(".", "_")[-24:]

    # 1. Remove via MongoDB API
    client = _get_mongo_client()
    if client is not None:
        try:
            db = _get_db(client)
            db.users.update_one(
                {"userId": user_id},
                {
                    "$pull": {"fcmTokens": token},
                    "$unset": {f"devices.{device_key}": ""},
                },
            )
            logger.info(f"[Firestore-Mongo] Removed token for user_id={user_id}")
        except Exception as e:
            logger.warning(f"[Firestore-Mongo] Error removing token: {e}")

    # 2. Remove via Native Firebase Admin
    try:
        import firebase_admin
        if firebase_admin._apps:
            from firebase_admin import firestore
            fs = firestore.client()
            user_ref = fs.collection("users").document(user_id)
            user_ref.update({
                "fcmTokens": firestore.ArrayRemove([token]),
                f"devices.{device_key}": firestore.DELETE_FIELD,
            })
    except Exception as e:
        logger.debug(f"[Firestore-Native] Native remove bypassed: {e}")


def _prune_tokens_sync(user_id: str, tokens: List[str]) -> None:
    if not tokens:
        return

    # 1. Prune via MongoDB API
    client = _get_mongo_client()
    if client is not None:
        try:
            db = _get_db(client)
            db.users.update_one(
                {"userId": user_id},
                {"$pull": {"fcmTokens": {"$in": tokens}}},
            )
            logger.info(f"[Firestore-Mongo] Pruned {len(tokens)} stale token(s) for user_id={user_id}")
        except Exception as e:
            logger.warning(f"[Firestore-Mongo] Error pruning tokens: {e}")

    # 2. Prune via Native Firebase Admin
    try:
        import firebase_admin
        if firebase_admin._apps:
            from firebase_admin import firestore
            fs = firestore.client()
            user_ref = fs.collection("users").document(user_id)
            user_ref.update({
                "fcmTokens": firestore.ArrayRemove(tokens),
            })
    except Exception as e:
        logger.debug(f"[Firestore-Native] Native prune bypassed: {e}")


async def sync_token_to_firestore(user_id: str, token: str, device_name: str, platform: str) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _sync_token_sync, user_id, token, device_name, platform)


async def remove_token_from_firestore(user_id: str, token: str) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _remove_token_sync, user_id, token)


async def prune_tokens_from_firestore(user_id: str, tokens: List[str]) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _prune_tokens_sync, user_id, tokens)
