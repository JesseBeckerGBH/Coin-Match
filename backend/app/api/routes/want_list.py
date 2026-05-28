"""Want list routes — buyers specify what coins they're looking for."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.want_list import WantListItem
from app.schemas.want_list import WantListCreate, WantListResponse, WantListUpdate
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/want-list", tags=["want-list"])


@router.post("", response_model=WantListResponse)
def create_want(
    data: WantListCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a coin to your want list."""
    item = WantListItem(
        id=str(uuid.uuid4()),
        buyer_id=user.id,
        coin_type=data.coin_type,
        series=data.series,
        year_min=data.year_min,
        year_max=data.year_max,
        mint_marks=data.mint_marks,
        denomination=data.denomination,
        country=data.country,
        min_grade_numeric=data.min_grade_numeric,
        max_grade_numeric=data.max_grade_numeric,
        price_min=data.price_min,
        price_max=data.price_max,
        must_be_graded=data.must_be_graded,
        accept_ai_graded=data.accept_ai_graded,
        tags=data.tags,
        notes=data.notes,
        notify_immediately=data.notify_immediately,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return WantListResponse.model_validate(item)


@router.get("", response_model=List[WantListResponse])
def list_wants(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all items on your want list."""
    items = (
        db.query(WantListItem)
        .filter(WantListItem.buyer_id == user.id)
        .order_by(WantListItem.created_at.desc())
        .all()
    )
    return [WantListResponse.model_validate(i) for i in items]


@router.put("/{item_id}", response_model=WantListResponse)
def update_want(
    item_id: str,
    data: WantListUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a want-list item."""
    item = db.query(WantListItem).filter(
        WantListItem.id == item_id,
        WantListItem.buyer_id == user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Want-list item not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return WantListResponse.model_validate(item)


@router.delete("/{item_id}")
def delete_want(
    item_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a want-list item."""
    item = db.query(WantListItem).filter(
        WantListItem.id == item_id,
        WantListItem.buyer_id == user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Want-list item not found")

    db.delete(item)
    db.commit()
    return {"message": "Want-list item deleted", "id": item_id}
