
from itertools import combinations

from game.bidding import Bid, BID_VALUE_COUNTS
from game.hand_evaluator import HandRank, evaluate_five


CLAIM_CARD_COUNTS = {
    HandRank.HIGH_CARD: 1,
    HandRank.ONE_PAIR: 2,
    HandRank.TWO_PAIR: 4,
    HandRank.THREE_OF_A_KIND: 3,
    HandRank.STRAIGHT: 5,
    HandRank.FLUSH: 5,
    HandRank.FULL_HOUSE: 5,
    HandRank.FOUR_OF_A_KIND: 4,
    HandRank.STRAIGHT_FLUSH: 5,
    HandRank.ROYAL_FLUSH: 5,
}


def claim_exists(cards, bid):
    """
    Check whether a claimed poker combination
    exists among all the revealed cards.
    """

    if not isinstance(bid, Bid):
        raise TypeError("Expected a Bid object.")

    if len(cards) < CLAIM_CARD_COUNTS[bid.category]:
        return False

    # Flush uses custom bidding rules:
    # (Suit, Rank) means at least five cards of that
    # suit with ranks <= the declared rank, including
    # at least one card of the declared rank.
    if bid.category == HandRank.FLUSH:
        suit, high_card = bid.values

        qualifying_cards = [
            card
            for card in cards
            if card.suit == suit and card.rank <= high_card
        ]

        has_declared_high_card = any(
            card.rank == high_card
            for card in qualifying_cards
        )

        return (
            len(qualifying_cards) >= 5
            and has_declared_high_card
        )

    required = CLAIM_CARD_COUNTS[bid.category]
    value_count = BID_VALUE_COUNTS[bid.category]

    for combo in combinations(cards, required):
        result = evaluate_five(list(combo))

        if result[0] != bid.category:
            continue

        actual_values = tuple(result[1:1 + value_count])

        if actual_values == bid.values:
            return True

    return False
