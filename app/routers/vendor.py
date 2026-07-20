import asyncio
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.exceptions import BadRequestException, NotFoundException
from app.models import Category, KitchenSettings, MenuItem, Order, OrderItem, OrderStatus, StaffMember
from app.security import get_current_vendor
from app.sse import SSEConnectionManager, sse_manager
from app.vendor_schemas import KitchenUpdateRequest, MenuCreateRequest, MenuUpdateRequest, StaffRequest, StatusRequest
from app.cache import invalidate_menu_cache

router = APIRouter(prefix="/api/vendor", tags=["Vendor"])
vendor_stream = SSEConnectionManager()


def order_json(order: Order) -> dict:
    items_summary = ", ".join(
        f"{item.menu_item.name if item.menu_item else item.menu_item_id} x {item.quantity}"
        for item in order.items
    )
    student_name = order.user.name if order.user else "Student"
    placed_time = order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else None
    return {
        "id": str(order.id), "userId": order.user_id, "canteenId": str(order.canteen_id) if order.canteen_id else None, "status": order.status.value,
        "totalAmount": float(order.total_amount), "pickupNumber": order.pickup_number,
        "token": order.order_token or (str(order.pickup_number) if order.pickup_number is not None else str(order.id)[:8]),
        "studentName": student_name, "student_name": student_name,
        "rollNo": order.user_roll_number or "", "roll_no": order.user_roll_number or "",
        "branch": order.user.college if order.user and order.user.college else "",
        "itemsSummary": items_summary, "items_summary": items_summary,
        "total_amount": float(order.total_amount), "placed_time": placed_time,
        "scheduledDate": order.scheduled_date.isoformat() if order.scheduled_date else None,
        "scheduledSlotId": str(order.scheduled_slot_id) if order.scheduled_slot_id else None,
        "notes": order.notes, "createdAt": order.created_at.isoformat() if order.created_at else None,
        "items": [{"menuItemId": str(item.menu_item_id), "name": item.menu_item.name if item.menu_item else None,
                   "quantity": item.quantity, "price": str(item.price_at_time_of_order)} for item in order.items]
    }


@router.get("/orders")
async def orders(status: Optional[list[OrderStatus]] = Query(None), db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    query = select(Order).options(selectinload(Order.user), selectinload(Order.items).selectinload(OrderItem.menu_item)).where(Order.canteen_id == vendor.get("canteen_id")).order_by(Order.created_at.desc())
    if status:
        query = query.where(Order.status.in_(status))
    else:
        query = query.where(Order.status != OrderStatus.DELIVERED)
    result = await db.execute(query)
    return [order_json(item) for item in result.unique().scalars().all()]


@router.patch("/orders/{order_id}/status")
async def update_order(order_id: UUID, request: StatusRequest, db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    try:
        new_status = OrderStatus(request.status.upper())
    except ValueError:
        raise BadRequestException(f"Unsupported order status: {request.status}")
    result = await db.execute(select(Order).options(selectinload(Order.user), selectinload(Order.items).selectinload(OrderItem.menu_item)).where(Order.id == order_id, Order.canteen_id == vendor.get("canteen_id")))
    order = result.unique().scalar_one_or_none()
    if not order:
        raise NotFoundException(f"Order not found: {order_id}")
    order.status = new_status
    if new_status == OrderStatus.READY_FOR_PICKUP:
        order.actual_ready_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()
    payload = order_json(order)
    
    # 1. Broadcast to all active vendor dashboard apps
    await vendor_stream.broadcast_to_user("all", "order-status", payload)
    
    # 2. Cross-broadcast to customer order tracking app screens (real-time notification fix!)
    updated_at_str = datetime.now(timezone.utc).isoformat()
    if "." in updated_at_str:
        updated_at_str = updated_at_str.split(".")[0]
        
    await sse_manager.broadcast_to_user(order.user_id, "order-status", {
        "orderId": str(order.id),
        "userId": order.user_id,
        "status": order.status.value,
        "pickupNumber": order.pickup_number,
        "estimatedReadyAt": order.estimated_ready_at.isoformat() if order.estimated_ready_at else None,
        "updatedAt": updated_at_str
    })

    try:
        from app.pubsub import event_bridge
        await event_bridge.notify("order_status_updated", payload)
    except Exception as exc:
        print(f"[SSE Error] Failed to publish PostgreSQL event: {exc}")
    
    return payload


@router.get("/orders/stream")
async def stream_orders(vendor=Depends(get_current_vendor)):
    async def event_generator():
        queue = await vendor_stream.subscribe("all")
        try:
            yield {"event": "connected", "data": "ok"}
            while True:
                yield await queue.get()
        except asyncio.CancelledError:
            pass
        finally:
            vendor_stream.unsubscribe("all", queue)
    return EventSourceResponse(event_generator(), ping=30)


@router.get("/menu")
async def get_menu(db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    result = await db.execute(select(MenuItem).where(MenuItem.canteen_id == vendor.get("canteen_id")).order_by(MenuItem.name))
    seen = set()
    items = []
    for item in result.scalars().all():
        key = item.name
        if key in seen:
            continue
        seen.add(key)
        items.append(menu_json(item))
    return items


def menu_json(item: MenuItem) -> dict:
    category_id = str(item.category_id) if item.category_id else None
    price = float(item.price)
    return {"id": str(item.id), "name": item.name, "price": price, "canteenId": str(item.canteen_id) if item.canteen_id else None, "description": item.description,
            "categoryId": category_id, "category_id": category_id, "imageUrl": item.image_url, "image_url": item.image_url,
            "stock": item.stock, "isAvailable": item.is_available, "is_available": item.is_available,
            "isStudentVisible": item.is_student_visible, "is_student_visible": item.is_student_visible,
            "preparationTimeMinutes": item.preparation_time_minutes, "preparation_time_minutes": item.preparation_time_minutes}


@router.post("/menu", status_code=201)
async def create_menu(request: MenuCreateRequest, db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    item = MenuItem(name=request.name, price=request.price, category_id=request.category_id,
                    description=request.description, stock=request.stock or 0,
                    image_url=request.image_url, is_available=request.is_available if request.is_available is not None else True,
                    is_student_visible=request.is_student_visible if request.is_student_visible is not None else True,
                    preparation_time_minutes=request.preparation_time_minutes or 10,
                    canteen_id=vendor.get("canteen_id"))
    db.add(item)
    await db.commit()
    await db.refresh(item)
    await invalidate_menu_cache()
    return menu_json(item)


@router.patch("/menu/{item_id}")
async def update_menu(item_id: UUID, request: MenuUpdateRequest, db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id, MenuItem.canteen_id == vendor.get("canteen_id")))
    item = result.scalar_one_or_none()
    if not item:
        raise NotFoundException(f"Menu item not found: {item_id}")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    await invalidate_menu_cache()
    return menu_json(item)


@router.get("/kitchen/settings")
async def get_kitchen(db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    result = await db.execute(select(KitchenSettings).where(KitchenSettings.id == 1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = KitchenSettings(id=1)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return {"basePrepBufferMinutes": settings.base_prep_buffer_minutes, "maxConcurrentOrders": settings.max_concurrent_orders,
            "isAcceptingOrders": settings.is_accepting_orders,
            "useRollNumberAsOrderToken": settings.use_roll_number_as_order_token}


@router.patch("/kitchen/settings")
async def update_kitchen(request: KitchenUpdateRequest, db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    result = await db.execute(select(KitchenSettings).where(KitchenSettings.id == 1))
    settings = result.scalar_one_or_none() or KitchenSettings(id=1)
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    db.add(settings)
    await db.commit()
    return await get_kitchen(db, vendor)


@router.get("/staff")
async def get_staff(db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    result = await db.execute(select(StaffMember).where(StaffMember.canteen_id == vendor.get("canteen_id")).order_by(StaffMember.id))
    return [{"id": str(member.id), "name": member.name, "role": member.role, "status": member.status,
             "imageUrl": member.image_url, "image_url": member.image_url}
            for member in result.scalars().all()]


@router.post("/staff", status_code=201)
async def add_staff(request: StaffRequest, db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    member = StaffMember(**request.model_dump(), canteen_id=vendor.get("canteen_id"))
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return {"id": str(member.id), "name": member.name, "role": member.role, "status": member.status,
            "imageUrl": member.image_url, "image_url": member.image_url}
