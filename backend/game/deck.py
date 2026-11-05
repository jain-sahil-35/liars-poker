import random

from game.cards import Card, Rank, Suit


class Deck:

    def __init__(self):
        self.cards = []

        self._create_deck()
        self.shuffle()

    def _create_deck(self):
        """Generate all 52 unique cards."""

        self.cards = [
            Card(rank, suit)
            for suit in Suit
            for rank in Rank
        ]

    def shuffle(self):
        """Randomize the order of cards."""
        random.shuffle(self.cards)

    def draw(self):
        """Draw one card from the top of the deck."""

        if not self.cards:
            raise ValueError("Cannot draw from an empty deck!")

        return self.cards.pop()

    def deal(self, count):
        """Draw multiple cards."""

        if count < 0:
            raise ValueError("Card count cannot be negative!")

        if count > len(self.cards):
            raise ValueError("Not enough cards remaining in deck!")

        return [self.draw() for _ in range(count)]

    @property
    def remaining(self):
        """Return the number of cards remaining."""
        return len(self.cards)

    def reset(self):
        """Recreate and shuffle a fresh deck."""

        self._create_deck()
        self.shuffle()