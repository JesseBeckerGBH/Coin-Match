"""Auth routes — signup, login, Google OAuth."""

import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User, UserType, SubscriptionTier
from app.schemas.user import UserSignup, UserLogin, TokenResponse, UserResponse
from app.services.auth import (
    hash_password, verify_password, create_access_token, get_current_user,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
def signup(data: UserSignup, db: Session = Depends(get_db)):
    """Register a new user — buyer, estate_seller, or dealer."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user_type_map = {
        "buyer": UserType.BUYER,
        "estate_seller": UserType.ESTATE_SELLER,
        "dealer": UserType.DEALER,
        "active_seller": UserType.ACTIVE_SELLER,
    }
    utype = user_type_map.get(data.user_type, UserType.BUYER)

    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name,
        user_type=utype,
        acquisition_trigger=data.acquisition_trigger,
        tier=SubscriptionTier.FREE,
        role="admin" if data.email == settings.OWNER_EMAIL else "user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.email, user.role)
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login with email + password."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(user.id, user.email, user.role)
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse.model_validate(user)


# ──────────────────── Google OAuth ────────────────────

@router.get("/oauth/google")
def google_oauth_redirect():
    """Redirect to Google OAuth consent screen."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=501, detail="Google OAuth not configured")

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": f"{settings.APP_URL}/api/auth/oauth/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + "&".join(
        f"{k}={v}" for k, v in params.items()
    )
    return RedirectResponse(url)


@router.get("/oauth/google/callback")
async def google_oauth_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback — create or login user."""
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": f"{settings.APP_URL}/api/auth/oauth/google/callback",
                "grant_type": "authorization_code",
            },
        )
        token_data = token_resp.json()
        
        # Get user info
        info_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        info = info_resp.json()

    email = info["email"]
    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=info.get("name", email.split("@")[0]),
            google_id=info.get("id"),
            avatar_url=info.get("picture"),
            email_verified=info.get("verified_email", False),
            user_type=UserType.BUYER,
            tier=SubscriptionTier.FREE,
            role="admin" if email == settings.OWNER_EMAIL else "user",
        )
        db.add(user)
    else:
        user.google_id = info.get("id")
        user.avatar_url = info.get("picture")
        user.last_login_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.email, user.role)
    # Redirect to frontend with token
    return RedirectResponse(f"{settings.APP_URL}/auth/callback?token={token}")
