from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date, time
from typing import List, Optional, Any
from app.models import OrderStatus, TicketStatus


# ─────────────────────────────────────────────
# Base
# ─────────────────────────────────────────────

class CamelModel(BaseModel):
    """Base for response schemas — allows extra fields from DB ORM objects."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        extra="ignore",
    )


class CamelRequestModel(BaseModel):
    """Base for request (input) schemas — rejects unknown fields to prevent parameter pollution."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        extra="forbid",
    )


# ─────────────────────────────────────────────
# Category
# ─────────────────────────────────────────────

class CategoryResponse(CamelModel):
    id: UUID
    name: str
    icon_url: Optional[str] = None
    display_order: int
    is_active: bool = True
    item_count: Optional[int] = None  # populated in router
    updated_at: Optional[datetime] = None


# ─────────────────────────────────────────────
# TimeSlot (for scheduling)
# ─────────────────────────────────────────────

class TimeSlotResponse(CamelModel):
    id: UUID
    canteen_id: Optional[UUID] = None
    label: Optional[str] = None  # e.g., "Breakfast", "Lunch", "Evening Snacks", "Dinner"
    start_time: time
    end_time: time
    max_orders: int
    orders_booked: Optional[int] = 0
    orders_remaining: Optional[int] = 0
    is_available: Optional[bool] = True


class CreateTimeSlotRequest(CamelRequestModel):
    canteen_id: Optional[UUID] = None
    label: Optional[str] = Field(default=None, max_length=100)
    start_time: time
    end_time: time
    max_orders: int = Field(default=5, ge=1, le=50)


class UpdateTimeSlotRequest(CamelRequestModel):
    label: Optional[str] = Field(default=None, max_length=100)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    max_orders: Optional[int] = Field(default=None, ge=1, le=50)
    is_active: Optional[bool] = None


# ─────────────────────────────────────────────
# MenuItem
# ─────────────────────────────────────────────

class MenuItemResponse(CamelModel):
    id: UUID
    name: str
    price: Decimal
    original_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    category_id: Optional[UUID] = None
    canteen_id: Optional[UUID] = None
    image_url: Optional[str] = Field(None, serialization_alias="imageUrl")
    quantity: int = 0
    special_offer: bool = Field(False, serialization_alias="specialOffer")
    is_available: bool = True
    preparation_time_minutes: int = 10
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def populate_quantity(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "quantity" not in data and "stock" in data:
                data["quantity"] = data["stock"]
        return data


class MenuPageResponse(CamelModel):
    items: List[MenuItemResponse]
    total: int
    page: int
    limit: int
    has_more: bool


class MenuSyncResponse(CamelModel):
    categories: List[CategoryResponse]
    items: List[MenuItemResponse]
    server_time: datetime


# ─────────────────────────────────────────────
# Cart
# ─────────────────────────────────────────────

class AddToCartRequest(CamelRequestModel):
    menu_item_id: UUID
    quantity: int = Field(ge=1, le=99)

class BulkReplaceCartRequest(CamelRequestModel):
    items: List[AddToCartRequest]

class UpdateCartItemRequest(CamelRequestModel):
    quantity: int = Field(ge=1, le=99)

class CartItemResponse(CamelModel):
    id: UUID
    menu_item_id: UUID
    canteen_id: Optional[UUID] = None
    quantity: int
    # Flattened item details for convenience
    item_name: str
    item_price: Decimal
    item_original_price: Optional[Decimal] = None
    item_discount_percent: Optional[Decimal] = None
    item_image_url: Optional[str] = None
    item_is_available: bool = True
    line_total: Decimal

class CartResponse(CamelModel):
    items: List[CartItemResponse]
    subtotal: Decimal
    total_items: int

class CartValidateIssue(CamelModel):
    menu_item_id: UUID
    item_name: str
    issue: str  # "UNAVAILABLE" | "PRICE_CHANGED"
    old_price: Optional[Decimal] = None
    new_price: Optional[Decimal] = None

class CartValidateResponse(CamelModel):
    is_valid: bool
    issues: List[CartValidateIssue]
    current_total: Decimal


# ─────────────────────────────────────────────
# Order
# ─────────────────────────────────────────────

class CreateOrderItemRequest(CamelRequestModel):
    menu_item_id: UUID
    quantity: int = Field(ge=1, le=99)

class CreateOrderRequest(CamelRequestModel):
    # NOTE: user_id is intentionally NOT in this schema — it is derived from
    # the verified JWT (sub claim) server-side.  Clients must NOT send it.
    total_amount: Decimal
    notes: Optional[str] = Field(default=None, max_length=500)
    items: Optional[List[CreateOrderItemRequest]] = None  # If None, pull from cart
    scheduled_date: Optional[date] = None
    scheduled_slot_id: Optional[UUID] = None
    coupon_code: Optional[str] = Field(default=None, max_length=50)

class OrderItemResponse(CamelModel):
    id: UUID
    order_id: UUID
    menu_item_id: UUID
    item_name: Optional[str] = None   # Populated in router
    quantity: int
    price_at_time_of_order: Decimal
    line_total: Optional[Decimal] = None

class OrderResponse(CamelModel):
    id: UUID
    user_id: str
    canteen_id: Optional[UUID] = None
    user_roll_number: Optional[str] = None
    order_token: Optional[str] = None
    total_amount: Decimal
    discount_amount: Decimal = Decimal("0.00")
    coupon_code: Optional[str] = None
    status: OrderStatus
    pickup_number: Optional[int] = None
    pickup_date: Optional[date] = None
    estimated_ready_at: Optional[datetime] = None
    actual_ready_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    items: List[OrderItemResponse]
    scheduled_date: Optional[date] = None
    scheduled_slot_id: Optional[UUID] = None
    scheduled_slot: Optional[TimeSlotResponse] = None

class UpdateOrderStatusRequest(CamelRequestModel):
    status: OrderStatus

class OrderHistoryResponse(CamelModel):
    orders: List[OrderResponse]
    total: int
    page: int
    limit: int


# ─────────────────────────────────────────────
# Kitchen
# ─────────────────────────────────────────────

class KitchenStatusResponse(CamelModel):
    is_accepting_orders: bool
    active_orders_count: int
    estimated_wait_minutes: int
    message: str
    use_roll_number_as_order_token: bool = False

class EtaPreviewRequest(CamelModel):
    items: List[CreateOrderItemRequest]

class EtaPreviewResponse(CamelModel):
    estimated_ready_minutes: int
    estimated_ready_at: datetime
    base_prep_minutes: int
    queue_buffer_minutes: int


# ─────────────────────────────────────────────
# User & Auth
# ─────────────────────────────────────────────

class UserResponse(CamelModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    roll_number: Optional[str] = None
    college: Optional[str] = None
    college_id: Optional[UUID] = None
    preferred_canteen_id: Optional[UUID] = None
    use_roll_number_as_order_token: bool = False
    phone_verified: bool = False

class RegisterRequest(CamelRequestModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=7, max_length=128)
    phone: str = Field(min_length=1, max_length=20)
    roll_number: str = Field(min_length=1, max_length=50)
    college: str = Field(min_length=1, max_length=200)
    college_id: Optional[UUID] = None
    preferred_canteen_id: Optional[UUID] = None

class LoginRequest(CamelRequestModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)

class LoginResponse(CamelModel):
    access_token: str   # Short-lived (ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token: str  # Long-lived (REFRESH_TOKEN_EXPIRE_DAYS) — store securely
    token_type: str = "bearer"
    user: UserResponse


class RefreshRequest(CamelRequestModel):
    """Body for POST /api/auth/refresh."""
    refresh_token: str


class RefreshResponse(CamelModel):
    """Response from POST /api/auth/refresh — only a new access token."""
    access_token: str
    token_type: str = "bearer"


class StreamTicketResponse(CamelModel):
    """One-time ticket for SSE/WebSocket connections (avoids JWT in URL)."""
    ticket: str
    expires_in_seconds: int = 30


class RegistrationOtpResponse(CamelModel):
    verification_required: bool = True
    expires_in_minutes: int
    message: str


class VerifyRegistrationOtpRequest(CamelRequestModel):
    email: str = Field(min_length=5, max_length=254)
    otp: str = Field(min_length=4, max_length=6)


class ResendRegistrationOtpRequest(CamelRequestModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class UpdateProfileRequest(CamelRequestModel):
    name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    roll_number: Optional[str] = Field(default=None, min_length=1, max_length=50)
    college: Optional[str] = Field(default=None, min_length=1, max_length=200)
    college_id: Optional[UUID] = None
    preferred_canteen_id: Optional[UUID] = None
    use_roll_number_as_order_token: Optional[bool] = None


# ─────────────────────────────────────────────
# FAQ & Support
# ─────────────────────────────────────────────

class FaqItemResponse(CamelModel):
    id: UUID
    question: str
    answer: str

class FaqCategoryResponse(CamelModel):
    id: UUID
    title: str
    icon: Optional[str] = None
    display_order: int
    items: List[FaqItemResponse] = []

class CreateTicketRequest(CamelRequestModel):
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=2000)

class TicketResponse(CamelModel):
    id: UUID
    subject: str
    message: str
    status: TicketStatus
    created_at: datetime
