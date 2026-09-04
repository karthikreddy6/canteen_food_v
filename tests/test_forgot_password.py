import datetime
import hashlib
import secrets
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.models import User, PasswordResetOtp
from app.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordOtpResponse,
    VerifyResetOtpRequest,
    VerifyResetOtpResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.routers.auth import (
    mask_phone,
    find_user_by_identifier,
    create_and_send_reset_otp,
    forgot_password,
    verify_reset_otp,
    reset_password,
    otp_hash,
)
from app.security import (
    create_password_reset_token,
    verify_password_reset_token,
    hash_password,
    verify_password,
)
from app.exceptions import BadRequestException, NotFoundException


def _make_test_user(**kwargs):
    defaults = {
        "id": "usr-reset-123",
        "name": "Reset User",
        "email": "reset@example.com",
        "phone": "919876543210",
        "phone_verified": True,
        "token_version": 1,
        "refresh_token_version": 1,
        "refresh_token_hash": "existing-refresh-hash",
        "hashed_password": hash_password("OldPassword123"),
        "status": "active",
    }
    defaults.update(kwargs)
    return User(**defaults)


# ─── Schema Tests ─────────────────────────────────────────────

def test_mask_phone():
    assert mask_phone("919876543210") == "+91 ******3210"
    assert mask_phone("9876543210") == "******3210"
    assert mask_phone("123") == "****"


def test_forgot_password_request_validation():
    # Valid with identifier
    req1 = ForgotPasswordRequest(identifier="user@example.com")
    assert req1.identifier == "user@example.com"

    # Valid with email
    req2 = ForgotPasswordRequest(email="user@example.com")
    assert req2.email == "user@example.com"

    # Valid with phone
    req3 = ForgotPasswordRequest(phone="9876543210")
    assert req3.phone == "9876543210"

    # Invalid without any
    with pytest.raises(ValueError, match="Please provide an email or phone number"):
        ForgotPasswordRequest()


def test_forgot_password_otp_response_camel_case():
    resp = ForgotPasswordOtpResponse(
        message="Code sent",
        expires_in_minutes=5,
        masked_phone="+91 ******3210",
        fallback_otp="123456",
    )
    dumped = resp.model_dump(by_alias=True)
    assert dumped["maskedPhone"] == "+91 ******3210"
    assert dumped["expiresInMinutes"] == 5
    assert dumped["fallbackOtp"] == "123456"
    assert dumped["otpSent"] is True
    assert dumped["status"] == "otp_sent"


# ─── Security Token Tests ─────────────────────────────────────

def test_password_reset_token_roundtrip():
    token = create_password_reset_token("usr-123", token_version=1)
    payload = verify_password_reset_token(token)
    assert payload["sub"] == "usr-123"
    assert payload["ver"] == 1
    assert payload["type"] == "password_reset"


# ─── Identifier Lookup Tests ──────────────────────────────────

@pytest.mark.asyncio
async def test_find_user_by_identifier_email():
    user = _make_test_user(email="test@example.com")
    mock_db = AsyncMock()
    mock_scalar = MagicMock()
    mock_scalar.scalars().first.return_value = user
    mock_db.execute.return_value = mock_scalar

    found = await find_user_by_identifier(mock_db, "TEST@example.com")
    assert found == user


@pytest.mark.asyncio
async def test_find_user_by_identifier_phone_suffix():
    user = _make_test_user(phone="919876543210")
    mock_db = AsyncMock()
    # First exact search returns None, second 10-digit suffix search returns user
    scalar_exact = MagicMock()
    scalar_exact.scalars().first.return_value = None
    scalar_suffix = MagicMock()
    scalar_suffix.scalars().first.return_value = user

    mock_db.execute.side_effect = [scalar_exact, scalar_suffix]

    found = await find_user_by_identifier(mock_db, "9876543210")
    assert found == user


# ─── Endpoint: /forgot-password ───────────────────────────────

@pytest.mark.asyncio
async def test_forgot_password_sends_otp_to_registered_phone():
    user = _make_test_user(email="user@test.com", phone="919876543210")
    mock_db = AsyncMock()

    # User lookup mock
    user_result = MagicMock()
    user_result.scalars().first.return_value = user
    # Check existing OTP mock
    otp_result = MagicMock()
    otp_result.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [user_result, otp_result]

    mock_req = MagicMock()
    mock_req.client.host = "127.0.0.1"

    req_body = ForgotPasswordRequest(email="user@test.com")

    with patch("app.routers.auth.rate_limit_login", new=AsyncMock()), \
         patch("app.routers.auth.throttle_otp_per_phone", new=AsyncMock()), \
         patch("app.routers.auth.send_registration_otp", new=AsyncMock(return_value=True)):
        resp = await forgot_password(request=req_body, http_request=mock_req, db=mock_db)

    assert resp.otp_sent is True
    assert resp.status == "otp_sent"
    assert resp.masked_phone == "+91 ******3210"
    assert resp.fallback_otp is None
    assert mock_db.add.called
    added = mock_db.add.call_args[0][0]
    assert isinstance(added, PasswordResetOtp)
    assert added.user_id == user.id


@pytest.mark.asyncio
async def test_forgot_password_fallback_in_dev_mode():
    user = _make_test_user(email="user@test.com", phone="919876543210")
    mock_db = AsyncMock()

    user_result = MagicMock()
    user_result.scalars().first.return_value = user
    otp_result = MagicMock()
    otp_result.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [user_result, otp_result]

    mock_req = MagicMock()
    mock_req.client.host = "127.0.0.1"

    req_body = ForgotPasswordRequest(phone="9876543210")

    # When WhatsApp fails, falls back to last 6 digits: 543210
    with patch("app.routers.auth.rate_limit_login", new=AsyncMock()), \
         patch("app.routers.auth.throttle_otp_per_phone", new=AsyncMock()), \
         patch("app.routers.auth.send_registration_otp", new=AsyncMock(return_value=False)):
        resp = await forgot_password(request=req_body, http_request=mock_req, db=mock_db)

    assert resp.otp_sent is False
    assert resp.status == "otp_failed"
    assert resp.fallback_otp == "543210"


@pytest.mark.asyncio
async def test_forgot_password_unknown_account():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = None
    mock_db.execute.return_value = mock_result

    mock_req = MagicMock()
    mock_req.client.host = "127.0.0.1"

    req_body = ForgotPasswordRequest(email="nobody@example.com")

    with patch("app.routers.auth.rate_limit_login", new=AsyncMock()):
        with pytest.raises(NotFoundException, match="No account found"):
            await forgot_password(request=req_body, http_request=mock_req, db=mock_db)


@pytest.mark.asyncio
async def test_forgot_password_account_on_hold():
    user = _make_test_user(status="hold")
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = user
    mock_db.execute.return_value = mock_result

    mock_req = MagicMock()
    mock_req.client.host = "127.0.0.1"

    req_body = ForgotPasswordRequest(email="hold@example.com")

    with patch("app.routers.auth.rate_limit_login", new=AsyncMock()):
        with pytest.raises(BadRequestException, match="account is currently on hold"):
            await forgot_password(request=req_body, http_request=mock_req, db=mock_db)


# ─── Endpoint: /forgot-password/verify ────────────────────────

@pytest.mark.asyncio
async def test_verify_reset_otp_success_returns_reset_token():
    user = _make_test_user()
    verification = PasswordResetOtp(
        user_id=user.id,
        code_hash=otp_hash("543210"),
        expires_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(minutes=5),
        attempts=0,
    )

    mock_db = AsyncMock()
    user_result = MagicMock()
    user_result.scalars().first.return_value = user
    otp_result = MagicMock()
    otp_result.scalar_one_or_none.return_value = verification

    mock_db.execute.side_effect = [user_result, otp_result]

    mock_req = MagicMock()
    mock_req.client.host = "127.0.0.1"

    req_body = VerifyResetOtpRequest(email=user.email, otp="543210")

    with patch("app.routers.auth.rate_limit_login", new=AsyncMock()):
        resp = await verify_reset_otp(request=req_body, http_request=mock_req, db=mock_db)

    assert resp.status == "verified"
    assert resp.reset_token is not None
    # Token hash should be saved in DB
    expected_token_hash = hashlib.sha256(resp.reset_token.encode("utf-8")).hexdigest()
    assert verification.reset_token_hash == expected_token_hash


@pytest.mark.asyncio
async def test_verify_reset_otp_invalid_code_increments_attempts():
    user = _make_test_user()
    verification = PasswordResetOtp(
        user_id=user.id,
        code_hash=otp_hash("543210"),
        expires_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(minutes=5),
        attempts=1,
    )

    mock_db = AsyncMock()
    user_result = MagicMock()
    user_result.scalars().first.return_value = user
    otp_result = MagicMock()
    otp_result.scalar_one_or_none.return_value = verification

    mock_db.execute.side_effect = [user_result, otp_result]

    mock_req = MagicMock()
    mock_req.client.host = "127.0.0.1"

    req_body = VerifyResetOtpRequest(email=user.email, otp="000000")

    with patch("app.routers.auth.rate_limit_login", new=AsyncMock()):
        with pytest.raises(BadRequestException, match="Invalid verification code"):
            await verify_reset_otp(request=req_body, http_request=mock_req, db=mock_db)

    assert verification.attempts == 2


@pytest.mark.asyncio
async def test_verify_reset_otp_expired():
    user = _make_test_user()
    verification = PasswordResetOtp(
        user_id=user.id,
        code_hash=otp_hash("543210"),
        expires_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(minutes=1),
        attempts=0,
    )

    mock_db = AsyncMock()
    user_result = MagicMock()
    user_result.scalars().first.return_value = user
    otp_result = MagicMock()
    otp_result.scalar_one_or_none.return_value = verification

    mock_db.execute.side_effect = [user_result, otp_result]

    mock_req = MagicMock()
    mock_req.client.host = "127.0.0.1"

    req_body = VerifyResetOtpRequest(email=user.email, otp="543210")

    with patch("app.routers.auth.rate_limit_login", new=AsyncMock()):
        with pytest.raises(BadRequestException, match="Verification code has expired"):
            await verify_reset_otp(request=req_body, http_request=mock_req, db=mock_db)


# ─── Endpoint: /reset-password ────────────────────────────────

@pytest.mark.asyncio
async def test_reset_password_with_reset_token():
    user = _make_test_user(token_version=1, refresh_token_version=1)
    reset_token = create_password_reset_token(user.id, token_version=1)
    token_hash = hashlib.sha256(reset_token.encode("utf-8")).hexdigest()

    verification = PasswordResetOtp(
        user_id=user.id,
        code_hash="dummy",
        expires_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(minutes=5),
        reset_token_hash=token_hash,
    )

    mock_db = AsyncMock()
    user_result = MagicMock()
    user_result.scalar_one_or_none.return_value = user
    otp_result = MagicMock()
    otp_result.scalar_one_or_none.return_value = verification

    mock_db.execute.side_effect = [user_result, otp_result]

    mock_req = MagicMock()
    mock_req.client.host = "127.0.0.1"

    req_body = ResetPasswordRequest(
        reset_token=reset_token,
        new_password="BrandNewPassword123",
    )

    with patch("app.routers.auth.rate_limit_login", new=AsyncMock()):
        resp = await reset_password(request=req_body, http_request=mock_req, db=mock_db)

    assert resp.success is True
    # Password must be updated and match new password
    assert verify_password("BrandNewPassword123", user.hashed_password)
    assert not verify_password("OldPassword123", user.hashed_password)
    # Token versions must be bumped to invalidate sessions
    assert user.token_version == 2
    assert user.refresh_token_version == 2
    assert user.refresh_token_hash is None
    # Reset OTP record must be deleted
    assert mock_db.delete.called
    assert mock_db.delete.call_args[0][0] == verification


@pytest.mark.asyncio
async def test_reset_password_token_reuse_rejected():
    user = _make_test_user()
    reset_token = create_password_reset_token(user.id, token_version=1)

    mock_db = AsyncMock()
    user_result = MagicMock()
    user_result.scalar_one_or_none.return_value = user
    # Verification record not found because it was already deleted after first use
    otp_result = MagicMock()
    otp_result.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [user_result, otp_result]

    mock_req = MagicMock()
    mock_req.client.host = "127.0.0.1"

    req_body = ResetPasswordRequest(
        reset_token=reset_token,
        new_password="AnotherPassword123",
    )

    with patch("app.routers.auth.rate_limit_login", new=AsyncMock()):
        with pytest.raises(BadRequestException, match="already been used"):
            await reset_password(request=req_body, http_request=mock_req, db=mock_db)


@pytest.mark.asyncio
async def test_reset_password_direct_with_otp():
    user = _make_test_user()
    verification = PasswordResetOtp(
        user_id=user.id,
        code_hash=otp_hash("654321"),
        expires_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(minutes=5),
        attempts=0,
    )

    mock_db = AsyncMock()
    user_result = MagicMock()
    user_result.scalars().first.return_value = user
    otp_result = MagicMock()
    otp_result.scalar_one_or_none.return_value = verification

    mock_db.execute.side_effect = [user_result, otp_result]

    mock_req = MagicMock()
    mock_req.client.host = "127.0.0.1"

    req_body = ResetPasswordRequest(
        identifier=user.email,
        otp="654321",
        new_password="DirectResetPassword123",
    )

    with patch("app.routers.auth.rate_limit_login", new=AsyncMock()):
        resp = await reset_password(request=req_body, http_request=mock_req, db=mock_db)

    assert resp.success is True
    assert verify_password("DirectResetPassword123", user.hashed_password)
    assert mock_db.delete.called
