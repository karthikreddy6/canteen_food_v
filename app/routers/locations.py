from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.exceptions import BadRequestException
from app.models import Campus, College, Canteen
from app.security import get_client_ip
from app.security_rules import rate_limit_college_suggest

router = APIRouter(prefix="/api/locations", tags=["Locations"])


# ─── Serializers ────────────────────────────────────────────

def college_json(item: College) -> dict:
    return {"id": str(item.id), "name": item.name, "isActive": item.is_active}


def canteen_json(item: Canteen) -> dict:
    return {"id": str(item.id), "name": item.name, "isActive": item.is_active}


# ─── Request Bodies ─────────────────────────────────────────

class SuggestCollegeRequest(BaseModel):
    name: str = Field(min_length=3, max_length=200)

    class Config:
        populate_by_name = True


async def _get_default_campus(db: AsyncSession) -> Campus:
    campus = (await db.execute(select(Campus).where(Campus.name == "Main Campus"))).scalar_one_or_none()
    if campus:
        return campus
    campus = Campus(name="Main Campus")
    db.add(campus)
    await db.flush()
    return campus


# ─── GET Endpoints ──────────────────────────────────────────

@router.get("/colleges")
async def list_colleges(db: AsyncSession = Depends(get_db)):
    """List all active colleges."""
    query = select(College).where(College.is_active == True).order_by(College.name)
    result = await db.execute(query)
    return [college_json(item) for item in result.scalars().all()]


@router.get("/canteens")
async def list_canteens(
    college_id: Optional[str] = Query(None, alias="collegeId"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all active canteens.
    Pass ?collegeId=<uuid> to filter by college (recommended after user picks college).
    """
    query = select(Canteen).where(Canteen.is_active == True).order_by(Canteen.name)
    if college_id and college_id.strip():
        try:
            cid = UUID(college_id.strip())
            query = query.join(Canteen.colleges).where(College.id == cid)
        except ValueError:
            pass
    result = await db.execute(query)
    return [canteen_json(item) for item in result.unique().scalars().all()]


@router.get("/colleges/{college_id}/canteens")
async def college_canteens(college_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get canteens linked to a specific college by ID (convenience shortcut)."""
    result = await db.execute(
        select(Canteen).join(Canteen.colleges).where(
            College.id == college_id, Canteen.is_active == True
        ).order_by(Canteen.name)
    )
    return [canteen_json(item) for item in result.unique().scalars().all()]


# ─── POST: Suggest a New College ────────────────────────────

@router.post("/colleges/suggest", status_code=201)
async def suggest_college(request: SuggestCollegeRequest, http_request: Request, db: AsyncSession = Depends(get_db)):
    """
    A student can suggest a new college if theirs is not in the list.
    The college is added as INACTIVE (is_active=False) so an admin must approve it.
    Returns the new college entry so the student can proceed with registration.
    """
    client_ip = get_client_ip(http_request)
    await rate_limit_college_suggest(client_ip)
    # Check if a college with the same name already exists
    existing = await db.execute(
        select(College).where(
            func.lower(College.name) == request.name.strip().lower()
        )
    )
    existing_college = existing.scalar_one_or_none()
    if existing_college:
        # Return the existing one (could be inactive/pending)
        return {
            **college_json(existing_college),
            "suggested": False,
            "pendingApproval": not existing_college.is_active,
            "message": "This college already exists. It may be pending admin approval." if not existing_college.is_active else "College found."
        }

    # Create new college as INACTIVE — admin must approve before it becomes searchable
    campus = await _get_default_campus(db)
    new_college = College(
        name=request.name.strip(),
        campus_id=campus.id,
        is_active=False  # Pending admin approval
    )
    db.add(new_college)
    await db.commit()
    await db.refresh(new_college)

    return {
        **college_json(new_college),
        "suggested": True,
        "pendingApproval": True,
        "message": f"'{new_college.name}' has been submitted for approval. You can continue registration using this college."
    }
