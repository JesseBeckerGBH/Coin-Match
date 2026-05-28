"""User profile routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserProfileUpdate
from app.services.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/users", tags=["users"])


@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: UserProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile."""
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/dashboard-stats")
def dashboard_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get dashboard stats for the current user."""
    from app.models.coin import Coin, CoinStatus
    from app.models.want_list import WantListItem
    from app.models.transaction import Transaction, Match

    stats = {
        "user_type": user.user_type.value,
        "tier": user.tier.value,
        "total_purchases": user.total_purchases,
        "total_sales": user.total_sales,
    }

    if user.user_type.value in ("buyer", "dealer"):
        stats["active_wants"] = db.query(WantListItem).filter(
            WantListItem.buyer_id == user.id,
            WantListItem.is_active == True,
        ).count()
        stats["pending_matches"] = db.query(Match).filter(
            Match.buyer_id == user.id,
            Match.status.in_(["pending", "notified"]),
        ).count()

    if user.user_type.value in ("active_seller", "estate_seller", "dealer"):
        stats["active_listings"] = db.query(Coin).filter(
            Coin.seller_id == user.id,
            Coin.status == CoinStatus.LISTED,
        ).count()
        stats["coins_sold"] = db.query(Coin).filter(
            Coin.seller_id == user.id,
            Coin.status == CoinStatus.SOLD,
        ).count()

    return stats


@router.get("/admin/users")
def list_all_users(
    page: int = 1,
    per_page: int = 50,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin: list all users."""
    total = db.query(User).count()
    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return {
        "users": [UserResponse.model_validate(u) for u in users],
        "total": total,
        "page": page,
        "per_page": per_page,
    }
