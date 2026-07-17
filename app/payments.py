"""Charge processing."""

from app.models import Customer


class ChargeError(Exception):
    pass


def _gateway_charge(card_id: str, amount_cents: int) -> dict:
    """Pretend to call the payment gateway."""
    return {"status": "succeeded", "card_id": card_id, "amount": amount_cents}


def charge_customer(customer: Customer, amount_cents: int) -> dict:
    """Charge the customer's default card."""
    if amount_cents <= 0:
        raise ChargeError("amount must be positive")
    card = customer.default_card()
    # BUG: card can be None (customer without a default card) -> AttributeError
    if card.expired:
        raise ChargeError(f"card ending {card.last4} is expired")
    return _gateway_charge(card.card_id, amount_cents)
