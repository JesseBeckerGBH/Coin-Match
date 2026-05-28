"""Stripe Connect integration — handles marketplace payments with tiered commissions.

Flow:
1. Seller onboards via Stripe Connect (gets a connected account)
2. Buyer pays → funds go to platform
3. Platform calculates commission
4. Remainder transferred to seller's connected account
"""

import stripe
from app.config import settings
from app.services.commission import calculate_commission, get_buyer_commission

stripe.api_key = settings.STRIPE_SECRET_KEY


# ──────────────────── Subscription Products ────────────────────

SUBSCRIPTION_PRODUCTS = {
    "pro": {
        "name": "CoinMatch Pro Collector",
        "price_monthly": 1900,  # $19.00 in cents
        "features": [
            "Early access to Fresh Estate Inventory (24h before free users)",
            "Lower buyer commission (1.5% vs 3.0%)",
            "Unlimited want-list items",
            "Price history & market trends",
            "Priority matching",
        ],
    },
    "dealer": {
        "name": "CoinMatch Dealer",
        "price_monthly": 9900,  # $99.00 in cents
        "features": [
            "Instant Fresh Estate Inventory alerts",
            "Lowest buyer commission (0.75%)",
            "Unlimited want-list items",
            "API access for bulk operations",
            "Dedicated support",
            "Analytics dashboard",
            "Batch listing tools",
        ],
    },
}


def create_connect_account(email: str, user_type: str = "individual") -> dict:
    """Create a Stripe Connect Express account for a seller.
    
    Sellers need a connected account to receive payouts.
    """
    account = stripe.Account.create(
        type="express",
        email=email,
        capabilities={
            "card_payments": {"requested": True},
            "transfers": {"requested": True},
        },
        metadata={"platform": "coinmatch", "user_type": user_type},
    )
    return {"account_id": account.id, "account": account}


def create_onboarding_link(account_id: str, return_url: str, refresh_url: str) -> str:
    """Generate a Stripe Connect onboarding link for a seller."""
    link = stripe.AccountLink.create(
        account=account_id,
        refresh_url=refresh_url,
        return_url=return_url,
        type="account_onboarding",
    )
    return link.url


def create_payment_intent(
    amount_cents: int,
    seller_connect_account_id: str,
    buyer_tier: str = "free",
    metadata: dict = None,
) -> dict:
    """Create a payment intent for a coin purchase.
    
    The commission is calculated and the seller's share is set as
    the transfer amount to their connected account.
    """
    sale_amount = amount_cents / 100.0
    
    # Seller commission (platform fee from seller side)
    seller_comm = calculate_commission(sale_amount)
    
    # Buyer commission (added on top, varies by subscription tier)
    buyer_comm = get_buyer_commission(sale_amount, buyer_tier)
    
    # Total the buyer pays = sale price + buyer commission
    total_buyer_pays = int((sale_amount + buyer_comm.platform_fee_usd) * 100)
    
    # Amount transferred to seller = sale price - seller commission
    seller_receives = int(seller_comm.seller_net_usd * 100)
    
    intent = stripe.PaymentIntent.create(
        amount=total_buyer_pays,
        currency="usd",
        transfer_data={
            "destination": seller_connect_account_id,
            "amount": seller_receives,
        },
        metadata={
            "sale_amount": sale_amount,
            "seller_commission_rate": seller_comm.commission_rate_pct,
            "seller_commission_usd": seller_comm.platform_fee_usd,
            "buyer_commission_rate": buyer_comm.commission_rate_pct,
            "buyer_commission_usd": buyer_comm.platform_fee_usd,
            **(metadata or {}),
        },
    )
    
    return {
        "payment_intent_id": intent.id,
        "client_secret": intent.client_secret,
        "total_buyer_pays": total_buyer_pays / 100,
        "seller_receives": seller_receives / 100,
        "platform_total_fee": seller_comm.platform_fee_usd + buyer_comm.platform_fee_usd,
    }


def create_subscription_checkout(
    customer_id: str,
    tier: str,
    success_url: str,
    cancel_url: str,
) -> str:
    """Create a Stripe Checkout session for a subscription."""
    product = SUBSCRIPTION_PRODUCTS.get(tier)
    if not product:
        raise ValueError(f"Unknown tier: {tier}")
    
    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": product["name"]},
                "recurring": {"interval": "month"},
                "unit_amount": product["price_monthly"],
            },
            "quantity": 1,
        }],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"tier": tier},
    )
    return session.url
