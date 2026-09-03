import pytest
from pydantic import ValidationError

from app.schemas import (
    RegisterRequest,
    UpdateProfileRequest,
    DeleteAccountResponse,
    UserResponse,
)


def test_register_request_college_id_validation():
    """Verify that roll_number (College ID) must be strictly 3 digits."""
    valid_payload = {
        "name": "Test Student",
        "email": "student@example.com",
        "password": "strongpassword123",
        "phone": "919876543210",
        "roll_number": "101",
        "college": "Engineering College",
    }
    # Valid 3-digit strings
    for valid_roll in ["101", "000", "999", "042"]:
        req = RegisterRequest(**{**valid_payload, "roll_number": valid_roll})
        assert req.roll_number == valid_roll

    # Invalid cases: alphanumeric, fewer than 3 digits, more than 3 digits
    for invalid_roll in ["1", "12", "1234", "22CS101", "abc", "12a", ""]:
        with pytest.raises(ValidationError):
            RegisterRequest(**{**valid_payload, "roll_number": invalid_roll})


def test_update_profile_request_college_id_validation():
    """Verify that UpdateProfileRequest enforces 3-digit roll_number if provided."""
    # None should be allowed (optional field)
    req = UpdateProfileRequest(name="Updated Name", roll_number=None)
    assert req.roll_number is None

    # Valid 3-digit roll number
    req_valid = UpdateProfileRequest(roll_number="502")
    assert req_valid.roll_number == "502"

    # Invalid roll numbers
    for invalid_roll in ["42", "1000", "CS101", "xyz"]:
        with pytest.raises(ValidationError):
            UpdateProfileRequest(roll_number=invalid_roll)


def test_delete_account_response_schema():
    """Verify DeleteAccountResponse defaults and serialization."""
    resp = DeleteAccountResponse(message="Account has been placed on hold.")
    assert resp.status == "hold"
    assert resp.message == "Account has been placed on hold."
    dumped = resp.model_dump(by_alias=True)
    assert dumped["status"] == "hold"


def test_user_response_has_status_field():
    """Verify UserResponse includes status field."""
    user_data = {
        "id": "usr-123",
        "name": "Test User",
        "email": "test@example.com",
        "status": "hold",
    }
    resp = UserResponse(**user_data)
    assert resp.status == "hold"


@pytest.mark.asyncio
async def test_delete_account_sets_user_status_to_hold():
    """Verify delete_account sets status='hold' and invalidates sessions."""
    from unittest.mock import AsyncMock, MagicMock
    from app.routers.auth import delete_account
    from app.models import User

    # Mock user in DB
    mock_user = User(
        id="usr-test-hold",
        name="Hold Tester",
        email="holdtester@example.com",
        status="active",
        token_version=1,
        refresh_token_version=1,
        refresh_token_hash="some-hash",
    )

    mock_db = AsyncMock()
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.first.return_value = mock_user
    mock_db.execute.return_value = mock_execute_result

    # Call delete_account
    res = await delete_account(db=mock_db, current_user_id="usr-test-hold")

    assert res.status == "hold"
    assert res.message == "Account has been placed on hold."
    assert mock_user.status == "hold"
    assert mock_user.token_version == 2
    assert mock_user.refresh_token_version == 2
    assert mock_user.refresh_token_hash is None
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_rejects_user_on_hold():
    """Verify login rejects users whose status is 'hold'."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from app.routers.auth import login
    from app.schemas import LoginRequest
    from app.security import UnauthenticatedException, hash_password
    from app.models import User

    hashed = hash_password("secret123")
    mock_user = User(
        id="usr-hold-login",
        name="Hold User",
        email="holdlogin@example.com",
        hashed_password=hashed,
        status="hold",
        phone_verified=True,
    )

    mock_db = AsyncMock()
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.first.return_value = mock_user
    mock_db.execute.return_value = mock_execute_result

    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"

    login_req = LoginRequest(email="holdlogin@example.com", password="secret123")

    with patch("app.routers.auth.verify_password_async", return_value=True):
        with pytest.raises(UnauthenticatedException) as exc_info:
            await login(request=login_req, http_request=mock_request, db=mock_db)

    assert "hold" in str(exc_info.value.message).lower()


@pytest.mark.asyncio
async def test_refresh_token_rejects_user_on_hold():
    """Verify refresh token endpoint rejects users whose status is 'hold'."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from app.routers.auth import refresh_access_token
    from app.schemas import RefreshRequest
    from app.security import UnauthenticatedException
    from app.models import User

    mock_user = User(
        id="usr-hold-refresh",
        name="Hold User",
        email="holdrefresh@example.com",
        status="hold",
        refresh_token_version=1,
    )

    mock_db = AsyncMock()
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.first.return_value = mock_user
    mock_db.execute.return_value = mock_execute_result

    refresh_req = RefreshRequest(refresh_token="valid.refresh.token")

    with patch("app.routers.auth._decode_token", return_value={"type": "refresh", "sub": "usr-hold-refresh", "ver": 1, "jti": "j1"}):
        with pytest.raises(UnauthenticatedException) as exc_info:
            await refresh_access_token(request=refresh_req, db=mock_db)

    assert "hold" in str(exc_info.value.message).lower()


@pytest.mark.asyncio
async def test_verified_user_dependency_rejects_user_on_hold():
    """Verify get_current_user_id_verified rejects users whose status is 'hold'."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from fastapi.security import HTTPAuthorizationCredentials
    from app.security import get_current_user_id_verified, UnauthenticatedException

    mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="dummy.access.token")

    mock_db = AsyncMock()
    # row with (token_version, status)
    mock_result = MagicMock()
    mock_result.first.return_value = (1, "hold")
    mock_db.execute.return_value = mock_result

    mock_session_local = MagicMock()
    mock_session_local.return_value.__aenter__.return_value = mock_db

    with patch("app.security._decode_token", return_value={"type": "access", "sub": "usr-hold-access", "ver": 1}), \
         patch("app.database.AsyncSessionLocal", mock_session_local):
        with pytest.raises(UnauthenticatedException) as exc_info:
            await get_current_user_id_verified(credentials=mock_credentials)

    assert "hold" in str(exc_info.value.message).lower()


