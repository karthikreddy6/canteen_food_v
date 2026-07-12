import enum
import uuid
import datetime
from sqlalchemy import (
    Column, String, Numeric, Boolean, ForeignKey, DateTime,
    Integer, Enum, func, Text, Date, Time
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────

class OrderStatus(str, enum.Enum):
    PLACED = "PLACED"
    SCHEDULED = "SCHEDULED"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    DELIVERED = "DELIVERED"

class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


# ─────────────────────────────────────────────
# User
# ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    tickets = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# Category
# ─────────────────────────────────────────────

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    icon_url = Column(String, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)

    menu_items = relationship("MenuItem", back_populates="category")


# ─────────────────────────────────────────────
# TimeSlot (for order scheduling)
# ─────────────────────────────────────────────

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    max_orders = Column(Integer, nullable=False, default=5)
    is_active = Column(Boolean, nullable=False, default=True)


# ─────────────────────────────────────────────
# MenuItem
# ─────────────────────────────────────────────

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)          # Current selling price
    original_price = Column(Numeric(10, 2), nullable=True)  # Pre-discount price (for display)
    discount_percent = Column(Numeric(5, 2), nullable=True) # e.g. 10.00 = 10%
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    image_url = Column(String, nullable=True)
    special_offer = Column(Boolean, nullable=False, default=False, name="is_special_offer")
    is_available = Column(Boolean, nullable=False, default=True)
    preparation_time_minutes = Column(Integer, nullable=False, default=10)

    category = relationship("Category", back_populates="menu_items")
    cart_items = relationship("CartItem", back_populates="menu_item")


# ─────────────────────────────────────────────
# CartItem
# ─────────────────────────────────────────────

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime, nullable=False,
                      default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))

    user = relationship("User", back_populates="cart_items")
    menu_item = relationship("MenuItem", back_populates="cart_items", lazy="joined")


# ─────────────────────────────────────────────
# Order
# ─────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(OrderStatus, name="order_status"),
                    nullable=False, default=OrderStatus.PLACED)
    # Pickup counter number — resets daily
    pickup_number = Column(Integer, nullable=True)
    pickup_date = Column(Date, nullable=True)     # Date the pickup_number was assigned
    # ETA
    estimated_ready_at = Column(DateTime, nullable=True)
    actual_ready_at = Column(DateTime, nullable=True)
    # Scheduled pickup options
    scheduled_date = Column(Date, nullable=True)
    scheduled_slot_id = Column(UUID(as_uuid=True), ForeignKey("time_slots.id"), nullable=True)

    # User notes / special instructions
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False,
                        default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
                        server_default=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order",
                         cascade="all, delete-orphan", lazy="joined")
    scheduled_slot = relationship("TimeSlot", lazy="joined")


# ─────────────────────────────────────────────
# OrderItem
# ─────────────────────────────────────────────

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_time_of_order = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", lazy="joined")


# ─────────────────────────────────────────────
# KitchenSettings (single-row config table)
# ─────────────────────────────────────────────

class KitchenSettings(Base):
    __tablename__ = "kitchen_settings"

    id = Column(Integer, primary_key=True, default=1)   # Always row id=1
    base_prep_buffer_minutes = Column(Integer, nullable=False, default=3)
    max_concurrent_orders = Column(Integer, nullable=False, default=20)
    is_accepting_orders = Column(Boolean, nullable=False, default=True)


# ─────────────────────────────────────────────
# FAQ
# ─────────────────────────────────────────────

class FaqCategory(Base):
    __tablename__ = "faq_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    icon = Column(String, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)

    items = relationship("FaqItem", back_populates="category",
                         cascade="all, delete-orphan")


class FaqItem(Base):
    __tablename__ = "faq_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("faq_categories.id"), nullable=False)
    question = Column(String, nullable=False)
    answer = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    category = relationship("FaqCategory", back_populates="items")


# ─────────────────────────────────────────────
# Support Ticket
# ─────────────────────────────────────────────

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus, name="ticket_status"),
                    nullable=False, default=TicketStatus.OPEN)
    created_at = Column(DateTime, nullable=False,
                        default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))

    user = relationship("User", back_populates="tickets")
