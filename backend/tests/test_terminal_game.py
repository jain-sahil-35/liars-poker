from game.terminal_game import get_human_bid
from game.hand_evaluator import HandRank
from game.cards import Suit, Rank

def test_human_can_make_high_card_bid():

    inputs = iter(["1", "A"])

    bid = get_human_bid(
        current_bid=None,
        input_fn=lambda prompt: next(inputs)
    )

    assert bid.category == HandRank.HIGH_CARD
    assert bid.values == (14,)


def test_human_can_make_two_pair_bid():
    inputs = iter(["3", "A", "10"])

    bid = get_human_bid(
        current_bid=None,
        input_fn=lambda prompt: next(inputs)
    )

    assert bid.category == HandRank.TWO_PAIR
    assert bid.values == (14, 10)


def test_human_can_make_flush_bid():
    inputs = iter(["6", "1", "Q"])

    bid = get_human_bid(
        current_bid=None,
        input_fn=lambda prompt: next(inputs)
    )

    assert bid.category == HandRank.FLUSH
    assert bid.values == (Suit.HEARTS, Rank.QUEEN)


def test_human_can_make_full_house_bid():
    inputs = iter(["7", "7", "A"])

    bid = get_human_bid(
        current_bid=None,
        input_fn=lambda prompt: next(inputs)
    )

    assert bid.category == HandRank.FULL_HOUSE
    assert bid.values == (7, 14)


def test_human_can_make_royal_flush_bid():
    inputs = iter(["10"])

    bid = get_human_bid(
        current_bid=None,
        input_fn=lambda prompt: next(inputs)
    )

    assert bid.category == HandRank.ROYAL_FLUSH
    assert bid.values == ()