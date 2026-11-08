
from collections import Counter
from itertools import combinations
from enum import IntEnum


class HandRank(IntEnum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


def evaluate_five(cards):
    """
    Evaluate a hand containing 1 to 5 cards.

    Returns a tuple:
    (hand category, tie-breaker values...)
    """

    if not 1 <= len(cards) <= 5:
        raise ValueError("Hand must contain between 1 and 5 cards.")

    ranks = sorted(
        [int(card.rank) for card in cards],
        reverse=True
    )

    suits = [card.suit for card in cards]

    counts = Counter(ranks)

    # Sort by frequency first, then rank.
    # Example: [(3, 14), (2, 13)]
    groups = sorted(
        [(count, rank) for rank, count in counts.items()],
        reverse=True
    )

    is_flush = (
        len(cards) == 5
        and len(set(suits)) == 1
    )

    # Check for a normal five-card straight.
    # Ace-low (A, 2, 3, 4, 5) is not permitted.
    unique_ranks = sorted(set(ranks), reverse=True)

    is_straight = False
    straight_high = 0

    if len(cards) == 5 and len(unique_ranks) == 5:
        if unique_ranks[0] - unique_ranks[-1] == 4:
            is_straight = True
            straight_high = unique_ranks[0]

    # Royal Flush
    if is_flush and is_straight and straight_high == 14:
        return (HandRank.ROYAL_FLUSH,)

    # Straight Flush
    if is_flush and is_straight:
        return (HandRank.STRAIGHT_FLUSH, straight_high)

    # Four of a Kind
    if groups[0][0] == 4:
        return (
            HandRank.FOUR_OF_A_KIND,
            groups[0][1],
            groups[1][1] if len(groups) > 1 else 0
        )

    # Full House
    if len(groups) >= 2 and groups[0][0] == 3 and groups[1][0] == 2:
        return (
            HandRank.FULL_HOUSE,
            groups[0][1],
            groups[1][1]
        )

    # Flush
    if is_flush:
        return (HandRank.FLUSH, *ranks)

    # Straight
    if is_straight:
        return (HandRank.STRAIGHT, straight_high)

    # Three of a Kind
    if groups[0][0] == 3:
        kickers = sorted(
            [rank for count, rank in groups[1:]],
            reverse=True
        )

        return (
            HandRank.THREE_OF_A_KIND,
            groups[0][1],
            *kickers
        )

    # Two Pair
    if len(groups) >= 2 and groups[0][0] == 2 and groups[1][0] == 2:
        return (
            HandRank.TWO_PAIR,
            groups[0][1],
            groups[1][1],
            groups[2][1] if len(groups) > 2 else 0
        )

    # One Pair
    if groups[0][0] == 2:
        kickers = sorted(
            [rank for count, rank in groups[1:]],
            reverse=True
        )

        return (
            HandRank.ONE_PAIR,
            groups[0][1],
            *kickers
        )

    # High Card
    return (HandRank.HIGH_CARD, *ranks)


def evaluate_hand(cards):
    """
    Find the strongest poker hand available.

    If more than 5 cards are provided, examine
    every possible 5-card combination.
    """

    if not cards:
        raise ValueError("Cannot evaluate an empty hand.")

    if len(cards) <= 5:
        return evaluate_five(cards)

    best_hand = max(
        evaluate_five(list(combo))
        for combo in combinations(cards, 5)
    )

    return best_hand
