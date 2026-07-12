from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import KitchenStatusResponse, EtaPreviewRequest, EtaPreviewResponse
from app.services.eta import get_kitchen_settings, count_active_orders, calculate_eta

router = APIRouter(prefix="/api/kitchen", tags=["Kitchen"])


@router.get("/status", response_model=KitchenStatusResponse)
async def get_kitchen_status(db: AsyncSession = Depends(get_db)):
    """
    Returns current kitchen status: open/closed, active orders count,
    and estimated wait for a new order right now.
    """
    settings = await get_kitchen_settings(db)
    active_count = await count_active_orders(db)

    # Simple single-item ETA to estimate current wait
    wait_minutes = settings.base_prep_buffer_minutes * max(0, active_count) + 10

    if not settings.is_accepting_orders:
        message = "Kitchen is currently closed. Please try again later."
    elif active_count >= settings.max_concurrent_orders:
        message = "Kitchen is very busy. Orders temporarily paused."
        settings.is_accepting_orders = False
    elif wait_minutes > 30:
        message = f"High demand — estimated wait is {wait_minutes} minutes."
    else:
        message = f"We're open! Estimated wait: {wait_minutes} minutes."

    return KitchenStatusResponse(
        is_accepting_orders=settings.is_accepting_orders and active_count < settings.max_concurrent_orders,
        active_orders_count=active_count,
        estimated_wait_minutes=wait_minutes,
        message=message
    )


@router.post("/eta", response_model=EtaPreviewResponse)
async def preview_eta(
    request: EtaPreviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Preview estimated ready time BEFORE placing order.
    Call this when user views cart to show expected wait.
    """
    menu_item_ids = [item.menu_item_id for item in request.items]
    eta_data = await calculate_eta(db, menu_item_ids)

    return EtaPreviewResponse(
        estimated_ready_minutes=eta_data["estimated_minutes"],
        estimated_ready_at=eta_data["estimated_ready_at"],
        base_prep_minutes=eta_data["base_prep_minutes"],
        queue_buffer_minutes=eta_data["queue_buffer_minutes"]
    )
