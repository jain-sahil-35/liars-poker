import pytest

from game.bidding import Bid, BidManager
from game.hand_evaluator import HandRank


def test_bid_comparison():

    ace_high = Bid(HandRank.HIGH_CARD, (14,))
    pair_kings = Bid(HandRank.ONE_PAIR, (13,))
    pair_aces = Bid(HandRank.ONE_PAIR, (14,))

    assert ace_high < pair_kings
    assert pair_kings < pair_aces


def test_higher_bid_accepted():

    manager = BidManager()

    first = Bid(HandRank.HIGH_CARD, (14,))
    second = Bid(HandRank.ONE_PAIR, (13,))

    assert manager.place_bid(first) is True
    assert manager.place_bid(second) is True


def test_lower_bid_rejected():

    manager = BidManager()

    manager.place_bid(
        Bid(HandRank.ONE_PAIR, (13,))
    )

    with pytest.raises(ValueError):
        manager.place_bid(
            Bid(HandRank.HIGH_CARD, (14,))
        )


def test_equal_bid_rejected():

    manager = BidManager()

    bid = Bid(HandRank.ONE_PAIR, (13,))

    manager.place_bid(bid)

    with pytest.raises(ValueError):
        manager.place_bid(bid)


def test_cannot_call_without_bid():

    manager = BidManager()

    with pytest.raises(ValueError):
        manager.call_bullshit()


def test_call_bullshit_returns_current_bid():

    manager = BidManager()

    bid = Bid(HandRank.ONE_PAIR, (13,))

    manager.place_bid(bid)

    assert manager.call_bullshit() == bid


def test_reset_bidding():

    manager = BidManager()

    manager.place_bid(
        Bid(HandRank.ONE_PAIR, (13,))
    )

    manager.reset()

    assert manager.current_bid is None


def test_invalid_rank_rejected():

    with pytest.raises(ValueError):
        Bid(HandRank.ONE_PAIR, (15,))


def test_bid_requires_rank_values():

    with pytest.raises(ValueError):
        Bid(HandRank.ONE_PAIR, ())