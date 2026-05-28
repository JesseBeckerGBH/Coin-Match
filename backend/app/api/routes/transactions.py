"""Transaction routes — purchases, payments, shipping."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.coin import Coin, CoinStatus
from app.models.transaction import Transaction, TransactionStatus
from app.schemas.transaction import (
    TransactionResponse, PurchaseRequest, ShippingUpdate, CommissionEstimate,
)
from app.services.auth import get_current_user
from app.services.commission import calculate_commission, get_buyer_commission
from app.services.stripe_connect import create_payment_intent

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("/estimate-commission", response_model=CommissionEstimate)
def estimate_commission(amount: float):
    """Preview the seller commission for a given sale amount."""
    result = calculate_commission(amount)
    return CommissionEstimate(
        sale_amount=result.sale_amount,
        commission_rate=result.commission_rate,
        commission_rate_pct=result.commission_rate_pct,
        platform_fee_usd=result.platform_fee_usd,
        seller_net_usd=result.seller_net_usd,
    )


@router.post("/purchase")
def purchase_coin(
    data: PurchaseRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Initiate a purchase — creates a Stripe payment intent."""
    coin = db.query(Coin).filter(Coin.id == data.coin_id).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    if coin.status != CoinStatus.LISTED:
        raise HTTPException(status_code=400, detail="Coin is not available for purchase")
    if coin.seller_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot buy your own coin")

    seller = db.query(User).filter(User.id == coin.seller_id).first()
    if not seller or not seller.stripe_connect_account_id:
        raise HTTPException(status_code=400, detail="Seller has not set up payments")

    price = data.offered_price or coin.asking_price or coin.estimated_value
    if not price or price <= 0:
        raise HTTPException(status_code=400, detail="No valid price for this coin")

    amount_cents = int(price * 100)
    
    # Create Stripe payment intent
    payment = create_payment_intent(
        amount_cents=amount_cents,
        seller_connect_account_id=seller.stripe_connect_account_id,
        buyer_tier=user.tier.value,
        metadata={
            "coin_id": coin.id,
            "buyer_id": user.id,
            "seller_id": seller.id,
        },
    )

    # Calculate commission for record
    seller_comm = calculate_commission(price)
    buyer_comm = get_buyer_commission(price, user.tier.value)

    # Create transaction record
    txn = Transaction(
        id=str(uuid.uuid4()),
        coin_id=coin.id,
        seller_id=seller.id,
        buyer_id=user.id,
        sale_amount=price,
        commission_rate=seller_comm.commission_rate,
        platform_fee=seller_comm.platform_fee_usd + buyer_comm.platform_fee_usd,
        seller_payout=seller_comm.seller_net_usd,
        stripe_payment_intent_id=payment["payment_intent_id"],
        status=TransactionStatus.PAYMENT_PENDING,
    )
    db.add(txn)

    coin.status = CoinStatus.PENDING_PAYMENT
    db.commit()

    return {
        "transaction_id": txn.id,
        "client_secret": payment["client_secret"],
        "total_buyer_pays": payment["total_buyer_pays"],
        "seller_receives": payment["seller_receives"],
        "platform_fee": payment["platform_total_fee"],
    }


@router.get("/my-purchases", response_model=List[TransactionResponse])
def my_purchases(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all transactions where the current user is the buyer."""
    txns = (
        db.query(Transaction)
        .filter(Transaction.buyer_id == user.id)
        .order_by(Transaction.created_at.desc())
        .all()
    )
    return [TransactionResponse.model_validate(t) for t in txns]


@router.get("/my-sales", response_model=List[TransactionResponse])
def my_sales(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all transactions where the current user is the seller."""
    txns = (
        db.query(Transaction)
        .filter(Transaction.seller_id == user.id)
        .order_by(Transaction.created_at.desc())
        .all()
    )
    return [TransactionResponse.model_validate(t) for t in txns]


@router.put("/{txn_id}/shipping", response_model=TransactionResponse)
def update_shipping(
    txn_id: str,
    data: ShippingUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Seller adds shipping info after payment is confirmed."""
    txn = db.query(Transaction).filter(
        Transaction.id == txn_id,
        Transaction.seller_id == user.id,
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    txn.tracking_number = data.tracking_number
    txn.shipping_carrier = data.shipping_carrier
    txn.shipped_at = datetime.now(timezone.utc)
    txn.status = TransactionStatus.SHIPPING
    db.commit()
    db.refresh(txn)
    return TransactionResponse.model_validate(txn)


@router.put("/{txn_id}/confirm-delivery")
def confirm_delivery(
    txn_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Buyer confirms delivery — completes the transaction."""
    txn = db.query(Transaction).filter(
        Transaction.id == txn_id,
        Transaction.buyer_id == user.id,
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    txn.delivered_at = datetime.now(timezone.utc)
    txn.completed_at = datetime.now(timezone.utc)
    txn.status = TransactionStatus.COMPLETED

    # Update coin status
    coin = db.query(Coin).filter(Coin.id == txn.coin_id).first()
    if coin:
        coin.status = CoinStatus.SOLD
        coin.sold_price = txn.sale_amount
        coin.sold_at = datetime.now(timezone.utc)

    # Update user stats
    seller = db.query(User).filter(User.id == txn.seller_id).first()
    buyer = db.query(User).filter(User.id == txn.buyer_id).first()
    if seller:
        seller.total_sales += 1
    if buyer:
        buyer.total_purchases += 1

    db.commit()
    return {"message": "Delivery confirmed. Transaction complete!", "transaction_id": txn.id}
