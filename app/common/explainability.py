"""Pure, deterministic risk assessment. No database access or machine learning."""

from decimal import Decimal

HISTORY_MULTIPLIER = Decimal("3")
NEW_CUSTOMER_THRESHOLD = Decimal("1000")
HISTORY_POINTS = 50
NEW_CUSTOMER_POINTS = 30
STOCK_POINTS = 20
MAX_SCORE = 100


def score_risk(
    total: Decimal,
    past_totals: list[Decimal],
    quantities_and_stock: list[tuple[int, int]],
) -> tuple[int, str]:
    score = 0
    reasons = []
    if past_totals and total > HISTORY_MULTIPLIER * sum(past_totals) / len(past_totals):
        score += HISTORY_POINTS
        reasons.append("Order total exceeds three times the customer's average past order total.")
    if not past_totals and total > NEW_CUSTOMER_THRESHOLD:
        score += NEW_CUSTOMER_POINTS
        reasons.append("Customer has no past orders and the order total exceeds 1000.")
    if any(quantity > stock for quantity, stock in quantities_and_stock):
        score += STOCK_POINTS
        reasons.append("At least one line quantity exceeds the product's declared stock.")
    return min(MAX_SCORE, score), " ".join(reasons) or "No risk rules were triggered."
