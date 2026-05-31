"""Tiered commission engine — rate INCREASES as sale value rises, per user request.

Schedule:
    $0 - $500       → 1.0%
    $501 - $2,000   → 2.0%
    $2,001 - $10,000 → 3.0%
    $10,001 - $50,000 → 4.0%
    $50,001+        → 5.0%
"""

from dataclasses import dataclass


COMMISSION_TIERS = [
    (500,       0.010),
    (2_000,     0.020),
    (10_000,    0.030),
    (50_000,    0.040),
    (float("inf"), 0.050),
]


@dataclass
class CommissionResult:
    sale_amount: float
    commission_rate: float
    commission_rate_pct: str
    platform_fee_usd: float
    seller_net_usd: float


def calculate_commission(sale_amount: float) -> CommissionResult:
    """Calculate tiered commission for a given sale amount.
    
    Args:
        sale_amount: Total sale price in USD.
        
    Returns:
        CommissionResult with rate, fee, and seller net.
    """
    if sale_amount <= 0:
        return CommissionResult(
            sale_amount=0,
            commission_rate=0,
            commission_rate_pct="0.00%",
            platform_fee_usd=0,
            seller_net_usd=0,
        )

    for threshold, rate in COMMISSION_TIERS:
        if sale_amount <= threshold:
            fee = round(sale_amount * rate, 2)
            return CommissionResult(
                sale_amount=round(sale_amount, 2),
                commission_rate=rate,
                commission_rate_pct=f"{rate * 100:.2f}%",
                platform_fee_usd=fee,
                seller_net_usd=round(sale_amount - fee, 2),
            )

    # Fallback (shouldn't reach here)
    rate = 0.01
    fee = round(sale_amount * rate, 2)
    return CommissionResult(
        sale_amount=round(sale_amount, 2),
        commission_rate=rate,
        commission_rate_pct="1.00%",
        platform_fee_usd=fee,
        seller_net_usd=round(sale_amount - fee, 2),
    )


def get_buyer_commission(sale_amount: float, tier: str) -> CommissionResult:
    """Buyer-side commission varies by subscription tier.
    
    Free buyer: 3.0%
    Pro collector: 1.5%
    Dealer: 0.75%
    """
    tier_rates = {
        "free": 0.030,
        "pro": 0.015,
        "dealer": 0.0075,
    }
    rate = tier_rates.get(tier, 0.030)
    fee = round(sale_amount * rate, 2)
    
    return CommissionResult(
        sale_amount=round(sale_amount, 2),
        commission_rate=rate,
        commission_rate_pct=f"{rate * 100:.2f}%",
        platform_fee_usd=fee,
        seller_net_usd=round(sale_amount - fee, 2),  # not really "seller net" here, but reuse struct
    )
