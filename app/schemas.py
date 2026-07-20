from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date, time
from typing import List, Optional
from app.models import OrderStatus, TicketStatus


# ─────────────────────────────────────────────
# Base
# ─────────────────────────────────────────────

class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
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
    start_time: time
    end_time: time
    max_orders: int
    orders_booked: Optional[int] = 0
    orders_remaining: Optional[int] = 0
    is_available: Optional[bool] = True


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
    special_offer: bool = Field(False, serialization_alias="specialOffer")
    is_available: bool = True
    preparation_time_minutes: int = 10
    updated_at: Optional[datetime] = None


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

class AddToCartRequest(CamelModel):
    menu_item_id: UUID
    quantity: int = Field(ge=1)

class UpdateCartItemRequest(CamelModel):
    quantity: int = Field(ge=1)

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

class CreateOrderItemRequest(CamelModel):
    menu_item_id: UUID
    quantity: int = Field(ge=1)

class CreateOrderRequest(CamelModel):
    user_id: str
    total_amount: Decimal
    notes: Optional[str] = None
    items: Optional[List[CreateOrderItemRequest]] = None  # If None, pull from cart
    scheduled_date: Optional[date] = None
    scheduled_slot_id: Optional[UUID] = None
    coupon_code: Optional[str] = None

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

class UpdateOrderStatusRequest(CamelModel):
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

class RegisterRequest(CamelModel):
    name: str
    email: str
    password: str
    phone: str = Field(min_length=1)
    roll_number: str = Field(min_length=1, max_length=50)
    college: str = Field(min_length=1, max_length=200)
    college_id: Optional[UUID] = None
    preferred_canteen_id: Optional[UUID] = None

class LoginRequest(CamelModel):
    email: str
    password: str

class LoginResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegistrationOtpResponse(CamelModel):
    verification_required: bool = True
    expires_in_minutes: int
    message: str


class VerifyRegistrationOtpRequest(CamelModel):
    email: str
    otp: str = Field(min_length=6, max_length=6)


class ResendRegistrationOtpRequest(CamelModel):
    email: str
    password: str


class UpdateProfileRequest(CamelModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
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

class CreateTicketRequest(CamelModel):
    subject: str
    message: str

class TicketResponse(CamelModel):
    id: UUID
    subject: str
    message: str
    status: TicketStatus
    created_at: datetime
