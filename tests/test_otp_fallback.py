import datetime
import secrets
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import httpx

from app.models import User, RegistrationOtp
from app.schemas import RegistrationOtpResponse, VerifyRegistrationOtpRequest
from app.routers.auth import (
    send_registration_otp,
    create_and_send_otp,
    verify_otp,
    otp_hash,
)
from app.exceptions import BadRequestException


def _make_test_user(**kwargs):
    defaults = {
        "id": "usr-test-123",
        "name": "Test User",
        "email": "test@example.com",
        "phone": "919876543210",
        "phone_verified": False,
        "token_version": 1,
        "refresh_token_version": 1,
        "use_roll_number_as_order_token": False,
        "reward_points_balance": 0,
        "lifetime_points_earned": 0,
        "is_premium": False,
        "status": "active",
    }
    defaults.update(kwargs)
    return User(**defaults)


def test_registration_otp_response_schema():
    """Verify RegistrationOtpResponse defaults and delivery_failed flag."""
    resp = RegistrationOtpResponse(
        expires_in_minutes=5,
        message="Verification code sent to your WhatsApp number.",
    )
    assert resp.verification_required is True
    assert resp.delivery_failed is False
    assert resp.otp_failed is False
    assert resp.otp_sent is True
    assert resp.status == "otp_sent"
    assert resp.fallback_otp is None
    dumped = resp.model_dump(by_alias=True)
    assert dumped["deliveryFailed"] is False
    assert dumped["otpFailed"] is False
    assert dumped["otpSent"] is True
    assert dumped["status"] == "otp_sent"
    assert dumped["fallbackOtp"] is None

    resp_failed = RegistrationOtpResponse(
        expires_in_minutes=5,
        message="Failed to send verification code. Your OTP is the last 6 digits of your phone number.",
        delivery_failed=True,
        otp_failed=True,
        otp_sent=False,
        status="otp_failed",
        fallback_otp="543210",
    )
    assert resp_failed.delivery_failed is True
    assert resp_failed.otp_failed is True
    assert resp_failed.otp_sent is False
    assert resp_failed.status == "otp_failed"
    assert resp_failed.fallback_otp == "543210"
    dumped_failed = resp_failed.model_dump(by_alias=True)
    assert dumped_failed["deliveryFailed"] is True
    assert dumped_failed["otpFailed"] is True
    assert dumped_failed["otpSent"] is False
    assert dumped_failed["status"] == "otp_failed"
    assert dumped_failed["fallbackOtp"] == "543210"


@pytest.mark.asyncio
async def test_send_registration_otp_not_configured():
    """When WHATSAPP_BOT_INTERNAL_KEY is not configured, returns False."""
    with patch("app.routers.auth.settings") as mock_settings:
        mock_settings.WHATSAPP_BOT_INTERNAL_KEY = None
        mock_settings.WHATSAPP_BOT_URL = "http://127.0.0.1:3000"
        result = await send_registration_otp("919876543210", "123456")
        assert result is False


@pytest.mark.asyncio
async def test_send_registration_otp_http_failure():
    """When HTTP request to WhatsApp bot fails, returns False."""
    with patch("app.routers.auth.settings") as mock_settings:
        mock_settings.WHATSAPP_BOT_INTERNAL_KEY = "test-key"
        mock_settings.WHATSAPP_BOT_URL = "http://127.0.0.1:3000"
        mock_settings.OTP_EXPIRY_MINUTES = 5

        with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
            result = await send_registration_otp("919876543210", "123456")
            assert result is False


@pytest.mark.asyncio
async def test_send_registration_otp_success():
    """When HTTP request to WhatsApp bot succeeds, returns True."""
    with patch("app.routers.auth.settings") as mock_settings:
        mock_settings.WHATSAPP_BOT_INTERNAL_KEY = "test-key"
        mock_settings.WHATSAPP_BOT_URL = "http://127.0.0.1:3000"
        mock_settings.OTP_EXPIRY_MINUTES = 5

        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None

        with patch("httpx.AsyncClient.post", return_value=mock_resp):
            result = await send_registration_otp("919876543210", "123456")
            assert result is True


@pytest.mark.asyncio
async def test_create_and_send_otp_failure_sets_last_six_digits():
    """When WhatsApp send fails, OTP stored is the last 6 digits of the phone number."""
    user = _make_test_user(phone="919876543210")

    mock_db = AsyncMock()
    mock_scalar = MagicMock()
    mock_scalar.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_scalar

    with patch("app.routers.auth.throttle_otp_per_phone", new=AsyncMock()), \
         patch("app.routers.auth.send_registration_otp", new=AsyncMock(return_value=False)):
        sent, message, fallback_otp = await create_and_send_otp(user, mock_db, is_resend=False)

    assert sent is False
    assert fallback_otp == "543210"
    assert "last 6 digits" in message
    assert mock_db.add.called
    added_otp = mock_db.add.call_args[0][0]
    assert isinstance(added_otp, RegistrationOtp)
    assert added_otp.code_hash == otp_hash("543210")


@pytest.mark.asyncio
async def test_create_and_send_otp_success_sets_random_code():
    """When WhatsApp send succeeds, OTP stored is the generated random code, not last 6 digits."""
    user = _make_test_user(phone="919876543210")

    mock_db = AsyncMock()
    mock_scalar = MagicMock()
    mock_scalar.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_scalar

    with patch("app.routers.auth.throttle_otp_per_phone", new=AsyncMock()), \
         patch("app.routers.auth.send_registration_otp", new=AsyncMock(return_value=True)):
        sent, message, fallback_otp = await create_and_send_otp(user, mock_db, is_resend=False)

    assert sent is True
    assert fallback_otp is None
    assert message == "Verification code sent to your WhatsApp number."
    assert mock_db.add.called
    added_otp = mock_db.add.call_args[0][0]
    assert isinstance(added_otp, RegistrationOtp)
    assert added_otp.code_hash != otp_hash("543210")


@pytest.mark.asyncio
async def test_verify_otp_with_fallback_last_six_digits():
    """When delivery failed and code_hash is last 6 digits, verifying with last 6 digits succeeds."""
    phone = "919876543210"
    last_six = "543210"

    user = _make_test_user(phone=phone)

    verification = RegistrationOtp(
        user_id=user.id,
        code_hash=otp_hash(last_six),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        attempts=0,
    )

    mock_db = AsyncMock()
    user_result = MagicMock()
    user_result.scalar_one_or_none.return_value = user

    otp_result = MagicMock()
    otp_result.scalar_one_or_none.return_value = verification

    mock_db.execute.side_effect = [user_result, otp_result]

    mock_req = MagicMock()
    mock_req.client.host = "127.0.0.1"

    req_body = VerifyRegistrationOtpRequest(email="test@example.com", otp=last_six)

    with patch("app.routers.auth.rate_limit_login", new=AsyncMock()):
        resp = await verify_otp(request=req_body, http_request=mock_req, db=mock_db)

    assert user.phone_verified is True
    assert resp.access_token is not None


@pytest.mark.asyncio
async def test_verify_otp_rejects_wrong_code():
    """When verifying with incorrect code, rejects with 400 BadRequestException."""
    phone = "919876543210"
    last_six = "543210"

    user = _make_test_user(phone=phone)

    verification = RegistrationOtp(
        user_id=user.id,
        code_hash=otp_hash(last_six),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        attempts=0,
    )

    mock_db = AsyncMock()
    user_result = MagicMock()
    user_result.scalar_one_or_none.return_value = user

    otp_result = MagicMock()
    otp_result.scalar_one_or_none.return_value = verification

    mock_db.execute.side_effect = [user_result, otp_result]

    mock_req = MagicMock()
    mock_req.client.host = "127.0.0.1"

    req_body = VerifyRegistrationOtpRequest(email="test@example.com", otp="000000")

    with patch("app.routers.auth.rate_limit_login", new=AsyncMock()):
        with pytest.raises(BadRequestException, match="Invalid verification code"):
            await verify_otp(request=req_body, http_request=mock_req, db=mock_db)

    assert verification.attempts == 1
    assert user.phone_verified is False
