from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_db
from app.models import FaqCategory, FaqItem, SupportTicket
from app.schemas import FaqCategoryResponse, FaqItemResponse, CreateTicketRequest, TicketResponse
from app.security import get_current_user_id
from app.exceptions import NotFoundException

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
    """Submit a new support ticket. Requires authentication."""
    ticket = SupportTicket(
        user_id=user_id,
        subject=request.subject,
        message=request.message
    )
    db.add(ticket)
    await db.flush()
    await db.commit()

    result = await db.execute(
        select(SupportTicket).where(SupportTicket.id == ticket.id)
    )
    saved = result.scalars().first()
    return TicketResponse.model_validate(saved)


@router.get("/tickets", response_model=List[TicketResponse])
async def get_my_tickets(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get all support tickets submitted by the current user."""
    result = await db.execute(
        select(SupportTicket)
        .where(SupportTicket.user_id == user_id)
        .order_by(SupportTicket.created_at.desc())
    )
    return [TicketResponse.model_validate(t) for t in result.scalars().all()]


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get a single support ticket by ID."""
    result = await db.execute(
        select(SupportTicket).where(
            SupportTicket.id == ticket_id,
            SupportTicket.user_id == user_id
        )
    )
    ticket = result.scalars().first()
    if not ticket:
        raise NotFoundException(f"Ticket not found: {ticket_id}")
    return TicketResponse.model_validate(ticket)
