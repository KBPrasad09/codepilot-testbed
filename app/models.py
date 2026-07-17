"""Customer and card data models."""

from dataclasses import dataclass, field


@dataclass
class Card:
    card_id: str
    last4: str
    expired: bool = False


@dataclass
class Customer:
    customer_id: str
    name: str
    cards: list = field(default_factory=list)
    default_card_id: str | None = None

    def default_card(self) -> Card | None:
        """Return the customer's default card, or None if they have none."""
        for card in self.cards:
            if card.card_id == self.default_card_id:
                return card
        return None
