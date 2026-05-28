"""Coin listing routes — CRUD, search, upload, grading."""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.coin import Coin, CoinStatus
from app.schemas.coin import (
    CoinCreate, CoinResponse, CoinListResponse, CoinSearchParams, GradeResult,
)
from app.services.auth import get_current_user
from app.services.matching import create_matches

router = APIRouter(prefix="/api/coins", tags=["coins"])


@router.post("", response_model=CoinResponse)
def create_coin(data: CoinCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new coin listing (draft state)."""
    coin = Coin(
        id=str(uuid.uuid4()),
        seller_id=user.id,
        title=data.title,
        description=data.description,
        year=data.year,
        mint_mark=data.mint_mark,
        denomination=data.denomination,
        coin_type=data.coin_type,
        series=data.series,
        country=data.country,
        asking_price=data.asking_price,
        metal_type=data.metal_type,
        weight_grams=data.weight_grams,
        purity=data.purity,
        provenance_notes=data.provenance_notes,
        tags=data.tags,
        status=CoinStatus.DRAFT,
        is_estate=(user.user_type.value == "estate_seller"),
    )
    db.add(coin)
    db.commit()
    db.refresh(coin)
    return CoinResponse.model_validate(coin)


@router.get("", response_model=CoinListResponse)
def list_coins(
    coin_type: Optional[str] = None,
    series: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    mint_mark: Optional[str] = None,
    min_grade: Optional[int] = None,
    max_grade: Optional[int] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    is_estate: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
):
    """Search and filter coin listings."""
    query = db.query(Coin).filter(Coin.status == CoinStatus.LISTED)

    if coin_type:
        query = query.filter(Coin.coin_type.ilike(f"%{coin_type}%"))
    if series:
        query = query.filter(Coin.series.ilike(f"%{series}%"))
    if year_min:
        query = query.filter(Coin.year >= year_min)
    if year_max:
        query = query.filter(Coin.year <= year_max)
    if mint_mark:
        query = query.filter(Coin.mint_mark == mint_mark.upper())
    if min_grade:
        query = query.filter(Coin.ai_grade_numeric >= min_grade)
    if max_grade:
        query = query.filter(Coin.ai_grade_numeric <= max_grade)
    if price_min:
        query = query.filter(
            (Coin.asking_price >= price_min) | (Coin.estimated_value >= price_min)
        )
    if price_max:
        query = query.filter(
            (Coin.asking_price <= price_max) | (Coin.estimated_value <= price_max)
        )
    if is_estate is not None:
        query = query.filter(Coin.is_estate == is_estate)

    total = query.count()

    # Sorting
    sort_col = getattr(Coin, sort_by, Coin.created_at)
    order_fn = desc if sort_order == "desc" else asc
    query = query.order_by(order_fn(sort_col))

    # Pagination
    offset = (page - 1) * per_page
    coins = query.offset(offset).limit(per_page).all()

    return CoinListResponse(
        coins=[CoinResponse.model_validate(c) for c in coins],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/fresh-inventory", response_model=CoinListResponse)
def fresh_inventory(
    page: int = 1,
    per_page: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fresh Estate Inventory — shows estate coins. Pro/Dealer get all, Free gets 24h-old only."""
    query = db.query(Coin).filter(
        Coin.status == CoinStatus.LISTED,
        Coin.is_estate == True,
    )

    # Free users only see estate coins listed 24+ hours ago
    if user.tier.value == "free":
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        query = query.filter(Coin.listed_at <= cutoff)

    total = query.count()
    offset = (page - 1) * per_page
    coins = query.order_by(desc(Coin.listed_at)).offset(offset).limit(per_page).all()

    return CoinListResponse(
        coins=[CoinResponse.model_validate(c) for c in coins],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{coin_id}", response_model=CoinResponse)
def get_coin(coin_id: str, db: Session = Depends(get_db)):
    """Get a single coin listing by ID."""
    coin = db.query(Coin).filter(Coin.id == coin_id).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    return CoinResponse.model_validate(coin)


@router.post("/{coin_id}/upload-images")
async def upload_images(
    coin_id: str,
    obverse: UploadFile = File(...),
    reverse: UploadFile = File(...),
    edge: Optional[UploadFile] = File(None),
    detail: Optional[UploadFile] = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload coin photos (minimum: obverse + reverse)."""
    coin = db.query(Coin).filter(Coin.id == coin_id, Coin.seller_id == user.id).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found or not yours")

    upload_dir = os.path.join(settings.UPLOAD_DIR, coin_id)
    os.makedirs(upload_dir, exist_ok=True)

    images = {}
    for label, file in [("obverse", obverse), ("reverse", reverse), ("edge", edge), ("detail", detail)]:
        if file and file.filename:
            ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
            filename = f"{label}.{ext}"
            filepath = os.path.join(upload_dir, filename)
            content = await file.read()
            
            if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                raise HTTPException(status_code=413, detail=f"{label} image too large (max {settings.MAX_UPLOAD_SIZE_MB}MB)")
            
            with open(filepath, "wb") as f:
                f.write(content)
            images[label] = f"/static/uploads/{coin_id}/{filename}"

    coin.images = images
    coin.status = CoinStatus.GRADING
    db.commit()

    return {"message": "Images uploaded", "images": images, "status": "grading"}


@router.post("/{coin_id}/grade", response_model=GradeResult)
def grade_coin(
    coin_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger AI grading for a coin. Requires images to be uploaded first."""
    coin = db.query(Coin).filter(Coin.id == coin_id, Coin.seller_id == user.id).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found or not yours")
    if not coin.images:
        raise HTTPException(status_code=400, detail="Upload images first")

    # TODO: Replace with actual AI grading model
    # For now, return a placeholder that demonstrates the API contract
    from engine.grading.grader import grade_coin_images
    
    result = grade_coin_images(coin.images, coin_type=coin.coin_type, year=coin.year)
    
    coin.ai_grade = result["grade"]
    coin.ai_grade_numeric = result["grade_numeric"]
    coin.ai_confidence = result["confidence"]
    coin.ai_luster_score = result["luster_score"]
    coin.ai_strike_score = result["strike_score"]
    coin.estimated_value = result.get("estimated_value")
    coin.status = CoinStatus.DRAFT  # Ready to list
    db.commit()

    return GradeResult(**result)


@router.post("/{coin_id}/list")
def list_coin(
    coin_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Publish a coin to the marketplace and trigger matching."""
    coin = db.query(Coin).filter(Coin.id == coin_id, Coin.seller_id == user.id).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found or not yours")
    if coin.status not in (CoinStatus.DRAFT, CoinStatus.GRADING):
        raise HTTPException(status_code=400, detail=f"Coin is already {coin.status.value}")
    if not coin.images:
        raise HTTPException(status_code=400, detail="Upload images before listing")

    coin.status = CoinStatus.LISTED
    coin.listed_at = datetime.now(timezone.utc)
    db.commit()

    # Trigger matching engine
    matches = create_matches(db, coin)

    return {
        "message": "Coin listed successfully",
        "coin_id": coin.id,
        "matches_found": len(matches),
        "status": "listed",
    }


@router.delete("/{coin_id}")
def withdraw_coin(
    coin_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Withdraw a coin listing."""
    coin = db.query(Coin).filter(Coin.id == coin_id, Coin.seller_id == user.id).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found or not yours")
    if coin.status in (CoinStatus.SOLD, CoinStatus.PENDING_PAYMENT):
        raise HTTPException(status_code=400, detail="Cannot withdraw — transaction in progress")

    coin.status = CoinStatus.WITHDRAWN
    db.commit()
    return {"message": "Coin withdrawn", "coin_id": coin.id}
