import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import FaqCategory, FaqItem, SupportTicket, SupportMessage, User, TicketStatus
from app.schemas import (
    FaqCategoryResponse, FaqItemResponse, CreateTicketRequest, TicketResponse,
    SupportMessageResponse, PostMessageRequest
)
from app.security import get_current_user_id
from app.exceptions import NotFoundException, BadRequestException
from app.services.support_service import support_client

router = APIRouter(prefix="/api/help", tags=["Help & FAQ"])


@router.get("/faq", response_model=List[FaqCategoryResponse])
async def get_all_faq(db: AsyncSession = Depends(get_db)):
    """Returns all FAQ categories with their active items nested inside."""
    result = await db.execute(
        select(FaqCategory).order_by(FaqCategory.display_order)
    )
    categories = result.scalars().all()

    responses = []
    for cat in categories:
        items_result = await db.execute(
            select(FaqItem)
            .where(FaqItem.category_id == cat.id, FaqItem.is_active == True)
        )
        items = items_result.scalars().all()
        cat_resp = FaqCategoryResponse(
            id=cat.id,
            title=cat.title,
            icon=cat.icon,
            display_order=cat.display_order,
            items=[FaqItemResponse(id=i.id, question=i.question, answer=i.answer) for i in items]
        )
        responses.append(cat_resp)

    return responses


@router.get("/faq/{category_id}", response_model=FaqCategoryResponse)
async def get_faq_category(category_id: str, db: AsyncSession = Depends(get_db)):
    """Returns a single FAQ category with its items."""
    result = await db.execute(
        select(FaqCategory).where(FaqCategory.id == category_id)
    )
    cat = result.scalars().first()
    if not cat:
        raise NotFoundException(f"FAQ category not found: {category_id}")

    items_result = await db.execute(
        select(FaqItem)
        .where(FaqItem.category_id == category_id, FaqItem.is_active == True)
    )
    items = items_result.scalars().all()

    return FaqCategoryResponse(
        id=cat.id,
        title=cat.title,
        icon=cat.icon,
        display_order=cat.display_order,
        items=[FaqItemResponse(id=i.id, question=i.question, answer=i.answer) for i in items]
    )


@router.post("/tickets", response_model=TicketResponse, status_code=201)
async def submit_ticket(
    request: CreateTicketRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Submit a support ticket. If a ticket for this order already exists, continues and reopens old ticket."""
    existing_ticket = None
    if request.order_id:
        existing_res = await db.execute(
            select(SupportTicket)
            .where(SupportTicket.user_id == user_id, SupportTicket.order_id == request.order_id)
            .order_by(SupportTicket.created_at.desc())
        )
        existing_ticket = existing_res.scalars().first()

    is_reopened = False
    if existing_ticket:
        ticket = existing_ticket
        is_reopened = True
        ticket.status = TicketStatus.OPEN
        ticket.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        ticket = SupportTicket(
            user_id=user_id,
            subject=request.subject,
            message=request.message,
            order_id=request.order_id,
            status=TicketStatus.OPEN,
        )
        db.add(ticket)
        await db.flush()

    # User message
    user_msg = SupportMessage(
        ticket_id=ticket.id,
        sender_type="USER",
        sender_id=user_id,
        sender_name="Customer",
        message=request.message,
        channel="APP",
    )
    db.add(user_msg)

    # Bot automated inquiry / acknowledgment
    if is_reopened:
        bot_prompt = "We've reopened your support request for this order. What seems to be the problem? Our support team will respond in a minute."
    else:
        bot_prompt = "Thanks for reaching out! What is the problem with your order? Our support team will respond in a minute."

    bot_msg = SupportMessage(
        ticket_id=ticket.id,
        sender_type="BOT",
        sender_id="buvva-assistant",
        sender_name="Buvva Assistant",
        message=bot_prompt,
        channel="APP",
    )
    db.add(bot_msg)
    await db.commit()

    # Forward to Support Desk & WhatsApp bot asynchronously in background
    user_res = await db.execute(select(User).where(User.id == user_id))
    user = user_res.scalars().first()
    user_phone = user.phone if user and user.phone else ""
    if user_phone:
        asyncio.create_task(support_client.create_support_ticket(
            user_phone=user_phone,
            category=request.subject,
            description=request.message,
            order_id=str(request.order_id) if request.order_id else None
        ))

    result = await db.execute(
        select(SupportTicket)
        .options(selectinload(SupportTicket.messages))
        .where(SupportTicket.id == ticket.id)
    )
    saved = result.scalars().first()
    return TicketResponse.model_validate(saved)


@router.patch("/tickets/{ticket_id}/resolve", response_model=TicketResponse)
async def resolve_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Mark a support ticket as resolved and notify the customer."""
    result = await db.execute(
        select(SupportTicket)
        .options(selectinload(SupportTicket.messages))
        .where(SupportTicket.id == ticket_id)
    )
    ticket = result.scalars().first()
    if not ticket:
        raise NotFoundException(f"Ticket not found: {ticket_id}")

    ticket.status = TicketStatus.RESOLVED
    ticket.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    resolve_notice = "Your issue for this order has been marked as resolved. If you need any further assistance, feel free to reply here!"
    bot_msg = SupportMessage(
        ticket_id=ticket.id,
        sender_type="BOT",
        sender_id="buvva-assistant",
        sender_name="Buvva Assistant",
        message=resolve_notice,
        channel="APP",
    )
    db.add(bot_msg)
    await db.commit()

    # Forward to WhatsApp/Support desk if user has phone
    user_res = await db.execute(select(User).where(User.id == ticket.user_id))
    user = user_res.scalars().first()
    if user and user.phone:
        asyncio.create_task(support_client.send_customer_message(
            phone=user.phone,
            message=f"✅ *Issue Resolved:*\n{resolve_notice}",
            channel="BOTH"
        ))

    await db.refresh(ticket)
    return TicketResponse.model_validate(ticket)


@router.get("/tickets", response_model=List[TicketResponse])
async def get_my_tickets(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get all support tickets submitted by the current user."""
    result = await db.execute(
        select(SupportTicket)
        .options(selectinload(SupportTicket.messages))
        .where(SupportTicket.user_id == user_id)
        .order_by(SupportTicket.created_at.desc())
    )
    return [TicketResponse.model_validate(t) for t in result.scalars().all()]


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get a single support ticket with all conversation messages."""
    result = await db.execute(
        select(SupportTicket)
        .options(selectinload(SupportTicket.messages))
        .where(
            SupportTicket.id == ticket_id,
            SupportTicket.user_id == user_id
        )
    )
    ticket = result.scalars().first()
    if not ticket:
        raise NotFoundException(f"Ticket not found: {ticket_id}")
    return TicketResponse.model_validate(ticket)


@router.get("/tickets/{ticket_id}/messages", response_model=List[SupportMessageResponse])
async def get_ticket_messages(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get all messages for a specific support ticket."""
    ticket_res = await db.execute(
        select(SupportTicket).where(
            SupportTicket.id == ticket_id,
            SupportTicket.user_id == user_id
        )
    )
    if not ticket_res.scalars().first():
        raise NotFoundException(f"Ticket not found: {ticket_id}")

    msg_res = await db.execute(
        select(SupportMessage)
        .where(SupportMessage.ticket_id == ticket_id)
        .order_by(SupportMessage.created_at.asc())
    )
    return [SupportMessageResponse.model_validate(m) for m in msg_res.scalars().all()]


@router.post("/tickets/{ticket_id}/messages", response_model=SupportMessageResponse, status_code=201)
async def post_ticket_message(
    ticket_id: UUID,
    payload: PostMessageRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Post a new customer message to an existing support ticket."""
    ticket_res = await db.execute(
        select(SupportTicket).where(
            SupportTicket.id == ticket_id,
            SupportTicket.user_id == user_id
        )
    )
    ticket = ticket_res.scalars().first()
    if not ticket:
        raise NotFoundException(f"Ticket not found: {ticket_id}")

    user_res = await db.execute(select(User).where(User.id == user_id))
    user = user_res.scalars().first()
    sender_name = payload.sender_name or (user.name if user else "Customer")

    msg = SupportMessage(
        ticket_id=ticket.id,
        sender_type="USER",
        sender_id=user_id,
        sender_name=sender_name,
        message=payload.message,
        channel="APP",
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    # Forward to Support Desk asynchronously in background
    if user and user.phone:
        asyncio.create_task(support_client.send_customer_message(
            phone=user.phone,
            message=payload.message,
            channel="APP"
        ))

    return SupportMessageResponse.model_validate(msg)
