import pytest

from app.models import Card, Customer
from app.payments import ChargeError, charge_customer


def customer_with_card() -> Customer:
    card = Card(card_id="c_1", last4="4242")
    return Customer(customer_id="cus_1", name="Alice", cards=[card], default_card_id="c_1")


def test_successful_charge():
    result = charge_customer(customer_with_card(), 500)
    assert result["status"] == "succeeded"


def test_rejects_non_positive_amount():
    with pytest.raises(ChargeError):
        charge_customer(customer_with_card(), 0)


def test_rejects_expired_card():
    customer = customer_with_card()
    customer.cards[0].expired = True
    with pytest.raises(ChargeError):
        charge_customer(customer, 500)
