import pytest

from game.bid_history import BidHistory
from game.bidding import Bid
from game.hand_evaluator import HandRank


def test_bid_history_starts_empty():
    history = BidHistory()

    assert len(history) == 0
    assert history.get_history() == []
    assert history.latest_bid() is None


def test_add_bid():
    history = BidHistory()
    bid = Bid(HandRank.ONE_PAIR, (10,))

    history.add_bid("player1", bid, 1)

    assert len(history) == 1
    assert history.latest_bid().bid == bid


def test_get_player_bids():
    history = BidHistory()

    bid1 = Bid(HandRank.ONE_PAIR, (10,))
    bid2 = Bid(HandRank.ONE_PAIR, (11,))
    bid3 = Bid(HandRank.THREE_OF_A_KIND, (5,))

    history.add_bid("player1", bid1, 1)
    history.add_bid("player2", bid2, 2)
    history.add_bid("player1", bid3, 3)

    player_bids = history.get_player_bids("player1")

    assert len(player_bids) == 2
    assert player_bids[0].bid == bid1
    assert player_bids[1].bid == bid3


def test_get_history_returns_copy():
    history = BidHistory()
    bid = Bid(HandRank.ONE_PAIR, (10,))

    history.add_bid("player1", bid, 1)

    records = history.get_history()
    records.clear()

    assert len(history) == 1


def test_latest_bid_returns_most_recent():
    history = BidHistory()

    bid1 = Bid(HandRank.ONE_PAIR, (10,))
    bid2 = Bid(HandRank.THREE_OF_A_KIND, (5,))

    history.add_bid("player1", bid1, 1)
    history.add_bid("player2", bid2, 2)

    assert history.latest_bid().bid == bid2


def test_reset_clears_history():
    history = BidHistory()
    bid = Bid(HandRank.ONE_PAIR, (10,))

    history.add_bid("player1", bid, 1)
    history.reset()

    assert len(history) == 0
    assert history.latest_bid() is None


def test_reject_invalid_bid():
    history = BidHistory()

    with pytest.raises(TypeError):
        history.add_bid("player1", "Pair of Kings", 1)


def test_reject_invalid_turn_number():
    history = BidHistory()
    bid = Bid(HandRank.ONE_PAIR, (10,))

    with pytest.raises(ValueError):
        history.add_bid("player1", bid, 0)