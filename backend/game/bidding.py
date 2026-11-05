from dataclasses import dataclass

from game.hand_evaluator import HandRank


@dataclass(frozen=True)
class Bid:

    category: HandRank
    values: tuple[int, ...]

    def __post_init__(self):

        if not self.values:
            raise ValueError("A bid must contain rank values.")

        if any(value < 2 or value > 14 for value in self.values):
            raise ValueError("Card ranks must be between 2 and 14.")

    @property
    def strength(self):
        """Return a comparable numerical representation."""

        return (int(self.category), *self.values)

    def __lt__(self, other):

        if not isinstance(other, Bid):
            return NotImplemented

        return self.strength < other.strength

    def __str__(self):

        names = {
            HandRank.HIGH_CARD: "High Card",
            HandRank.ONE_PAIR: "One Pair",
            HandRank.TWO_PAIR: "Two Pair",
            HandRank.THREE_OF_A_KIND: "Three of a Kind",
            HandRank.STRAIGHT: "Straight",
            HandRank.FLUSH: "Flush",
            HandRank.FULL_HOUSE: "Full House",
            HandRank.FOUR_OF_A_KIND: "Four of a Kind",
            HandRank.STRAIGHT_FLUSH: "Straight Flush",
            HandRank.ROYAL_FLUSH: "Royal Flush"
        }

        return f"{names[self.category]} - {self.values}"

class BidManager:

    def __init__(self):
        self.current_bid = None

    def place_bid(self, new_bid):

        if not isinstance(new_bid, Bid):
            raise TypeError("Expected a Bid object.")

        if self.current_bid is not None:

            if not self.current_bid < new_bid:
                raise ValueError(
                    "New bid must be higher than the current bid."
                )

        self.current_bid = new_bid

        return True

    def call_bullshit(self):

        if self.current_bid is None:
            raise ValueError(
                "Cannot call bullshit before a bid is made."
            )

        return self.current_bid

    def reset(self):
        """Reset bidding for a new round."""

        self.current_bid = None