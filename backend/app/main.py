"""CoinMatch — AI-Powered Numismatics Marketplace by JBAnalytics.

Connects coin collectors with estate sellers through AI grading
and intelligent buyer-seller matching. Lowest fees in the industry.
"""

import sys
import os

# Add project root to path for engine imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base

# Import models so tables are registered
from app.models.user import User
from app.models.coin import Coin
from app.models.want_list import WantListItem
from app.models.transaction import Transaction, Match, EstateEvent

# Import routers
from app.api.routes.auth import router as auth_router
from app.api.routes.coins import router as coins_router
from app.api.routes.want_list import router as want_list_router
from app.api.routes.transactions import router as transactions_router
from app.api.routes.billing import router as billing_router
from app.api.routes.users import router as users_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CoinMatch by JBAnalytics",
    description=(
        "AI-powered numismatics marketplace. Connects collectors with estate sellers "
        "through instant AI grading and intelligent matching. "
        "Lowest fees in the industry: 3% → 1% tiered commission ($10 minimum)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (coin images)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routers
app.include_router(auth_router)
app.include_router(coins_router)
app.include_router(want_list_router)
app.include_router(transactions_router)
app.include_router(billing_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {
        "name": "CoinMatch by JBAnalytics",
        "tagline": "AI-Powered Numismatics Marketplace",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "coinmatch-api",
        "version": "1.0.0",
    }
