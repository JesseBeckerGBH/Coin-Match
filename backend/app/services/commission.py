"""Tiered commission engine — hybrid model with minimum fee floor.

Sellers always pay the greater of $10 OR the tiered rate. This protects the
platform from losing money on tiny sales (Stripe + AI grading costs are roughly
constant per transaction) without overcharging small sellers, while still
delivering the headline 1.0% rate on high-value estate sales.

Schedule:
    $0 - $500       → 3.0%   (floor: $10)
    $501 - $2,000   → 2.5%
    $2,001 - $10,000 → 2.0%
    $10,001 - $50,000 → 1.5%
    $50,001+        → 1.0%
"""

from dataclasses import dataclass


MIN_FEE_USD = 10.0

COMMISSION_TIERS = [
    (500,          0.030),
    (2_000,        0.025),
    (10_000,       0.020),
    (50_000,       0.015),
    (float("inf"), 0.010),
]


@dataclass
class CommissionResult:
    sale_amount: float
    commission_rate: float
    commission_rate_pct: str
    platform_fee_usd: float
    seller_net_usd: float
    floor_applied: bool = False


def _tier_rate(sale_amount: float) -> float:
    for threshold, rate in COMMISSION_TIERS:
        if sale_amount <= threshold:
            return rate
    return COMMISSION_TIERS[-1][1]


def calculate_commission(sale_amount: float) -> CommissionResult:
    """Calculate hybrid commission: max($10, tiered rate)."""
    if sale_amount <= 0:
        return CommissionResult(
            sale_amount=0,
            commission_rate=0,
            commission_rate_pct="0.00%",
            platform_fee_usd=0,
            seller_net_usd=0,
        )

    rate = _tier_rate(sale_amount)
    tier_fee = round(sale_amount * rate, 2)
    fee = max(tier_fee, MIN_FEE_USD)
    floor_applied = fee > tier_fee
    effective_rate = fee / sale_amount

    return CommissionResult(
        sale_amount=round(sale_amount, 2),
        commission_rate=effective_rate,
        commission_rate_pct=f"{effective_rate * 100:.2f}%",
        platform_fee_usd=round(fee, 2),
        seller_net_usd=round(sale_amount - fee, 2),
        floor_applied=floor_applied,
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
        seller_net_usd=round(sale_amount - fee, 2),
    )
