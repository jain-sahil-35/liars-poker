
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
    HandRank.ROYAL_FLUSH: 5
}


def claim_exists(cards, bid):
    """
    Check whether a claimed poker combination
    exists among all the revealed cards.
    """

    if not isinstance(bid, Bid):
        raise TypeError("Expected a Bid object.")

    required = CLAIM_CARD_COUNTS[bid.category]

    # Flush claims count only cards of the declared suit
    # whose ranks are at or below the declared high card.
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

    if len(cards) < required:
        return False

    for combo in combinations(cards, required):

        result = evaluate_five(list(combo))

        if result[0] != bid.category:
            continue

        # Suit-specific categories must match the declared suit.
        if bid.category == HandRank.STRAIGHT_FLUSH:
            claimed_suit, high_rank = bid.values
            if not all(card.suit == claimed_suit for card in combo):
                continue
            if result[1] == high_rank:
                return True
            continue

        if bid.category == HandRank.ROYAL_FLUSH:
            claimed_suit = bid.values[0]
            if all(card.suit == claimed_suit for card in combo):
                return True
            continue

        value_count = BID_VALUE_COUNTS[bid.category]
        actual_values = tuple(result[1:1 + value_count])
        if actual_values == bid.values:
            return True

    return False
