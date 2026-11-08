
from dataclasses import dataclass

from game.cards import Rank, Suit
from game.hand_evaluator import HandRank


BID_VALUE_COUNTS = {
    HandRank.HIGH_CARD: 1,
    HandRank.ONE_PAIR: 1,
    HandRank.TWO_PAIR: 2,
    HandRank.THREE_OF_A_KIND: 1,
    HandRank.STRAIGHT: 1,
    HandRank.FLUSH: 2,
    HandRank.FULL_HOUSE: 2,
    HandRank.FOUR_OF_A_KIND: 1,
    HandRank.STRAIGHT_FLUSH: 2,
    HandRank.ROYAL_FLUSH: 1,
}


@dataclass(frozen=True)
class Bid:
    category: HandRank
    values: tuple

    def __post_init__(self):
        if not isinstance(self.category, HandRank):
            raise TypeError("Category must be a HandRank.")

        if len(self.values) != BID_VALUE_COUNTS[self.category]:
            raise ValueError(
                f"{self.category.name} requires "
                f"{BID_VALUE_COUNTS[self.category]} values."
            )

        # Flush: (Suit, Rank)
        if self.category == HandRank.FLUSH:
            suit, rank = self.values

            if not isinstance(suit, Suit):
                raise TypeError("Flush suit must be a Suit.")

            if not isinstance(rank, Rank):
                raise TypeError("Flush high card must be a Rank.")

            return

        # Straight Flush: (Suit, high_rank)
        if self.category == HandRank.STRAIGHT_FLUSH:
            suit, high_rank = self.values

            if not isinstance(suit, Suit):
                raise TypeError("Straight Flush suit must be a Suit.")

            if (
                not isinstance(high_rank, int)
                or isinstance(high_rank, bool)
                or high_rank < 6
                or high_rank > 13
            ):
                raise ValueError(
                    "Straight Flush high card must be between 6 and 13."
                )

            # Integer high-rank values are used consistently for straights.
            # 5-high is disallowed; 6-high is the lowest valid straight flush.
            # Ace-high is represented by the separate Royal Flush category.
            return

        # Royal Flush: (Suit,)
        if self.category == HandRank.ROYAL_FLUSH:
            if not isinstance(self.values[0], Suit):
                raise TypeError("Royal Flush suit must be a Suit.")

            return

        # All other categories use integer rank values.
        if any(
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 2
            or value > 14
            for value in self.values
        ):
            raise ValueError(
                "Card ranks must be integers between 2 and 14."
            )

        # Two Pair: higher pair must come first.
        if self.category == HandRank.TWO_PAIR:
            if self.values[0] <= self.values[1]:
                raise ValueError(
                    "Two Pair values must be in descending order."
                )

        # Ace-low Straights are not permitted.
        if self.category in (
            HandRank.STRAIGHT,
            HandRank.STRAIGHT_FLUSH
        ):
            if self.values[0] < 6:
                raise ValueError(
                    "The lowest allowed Straight is 6-high."
                )

    @property
    def strength(self):
        """Return a comparable numerical representation."""

        if self.category == HandRank.FLUSH:
            return (int(self.category), int(self.values[1]))
        
        if self.category == HandRank.STRAIGHT_FLUSH:
            # Suit identifies the claimed cards but does not affect bid strength.
            return (int(self.category), self.values[1])

        # Royal Flush suits have equal bidding strength.
        if self.category == HandRank.ROYAL_FLUSH:
            return (int(self.category),)

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
            HandRank.ROYAL_FLUSH: "Royal Flush",
        }

        if self.category == HandRank.FLUSH:
            suit, rank = self.values
            return f"Flush - {suit.value} - {rank.name}"

        if self.category == HandRank.STRAIGHT_FLUSH:
            suit, high_rank = self.values
            rank_names = {
                11: "Jack",
                12: "Queen",
                13: "King"
            }
            rank_name = rank_names.get(high_rank, str(high_rank))

            return f"Straight Flush - {suit.value} - {rank_name}-high"

        if self.category == HandRank.ROYAL_FLUSH:
            suit = self.values[0]
            return f"Royal Flush - {suit.value}"

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
