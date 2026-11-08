
import pytest

from game.bidding import Bid, BidManager
from game.cards import Rank, Suit
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

    manager.place_bid(Bid(HandRank.ONE_PAIR, (13,)))

    with pytest.raises(ValueError):
        manager.place_bid(Bid(HandRank.HIGH_CARD, (14,)))


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

    manager.place_bid(Bid(HandRank.ONE_PAIR, (13,)))
    manager.reset()

    assert manager.current_bid is None


def test_invalid_rank_rejected():
    with pytest.raises(ValueError):
        Bid(HandRank.ONE_PAIR, (15,))


def test_bid_requires_rank_values():
    with pytest.raises(ValueError):
        Bid(HandRank.ONE_PAIR, ())


def test_flush_requires_suit_and_rank():
    with pytest.raises(ValueError):
        Bid(HandRank.FLUSH, (Rank.QUEEN,))


def test_flush_requires_valid_suit():
    with pytest.raises(TypeError):
        Bid(HandRank.FLUSH, ("Hearts", Rank.QUEEN))


def test_flush_requires_valid_rank():
    with pytest.raises(TypeError):
        Bid(HandRank.FLUSH, (Suit.HEARTS, 12))


def test_flush_bids_of_different_suits_have_equal_strength():
    hearts = Bid(HandRank.FLUSH, (Suit.HEARTS, Rank.QUEEN))
    spades = Bid(HandRank.FLUSH, (Suit.SPADES, Rank.QUEEN))

    assert hearts.strength == spades.strength
    assert not hearts < spades
    assert not spades < hearts


def test_higher_flush_rank_is_a_higher_bid():
    flush_queen = Bid(HandRank.FLUSH, (Suit.HEARTS, Rank.QUEEN))
    flush_king = Bid(HandRank.FLUSH, (Suit.SPADES, Rank.KING))

    assert flush_queen < flush_king


def test_equal_flush_bids_are_rejected():
    manager = BidManager()

    hearts = Bid(HandRank.FLUSH, (Suit.HEARTS, Rank.QUEEN))
    spades = Bid(HandRank.FLUSH, (Suit.SPADES, Rank.QUEEN))

    manager.place_bid(hearts)

    with pytest.raises(ValueError):
        manager.place_bid(spades)


def test_five_high_straight_is_rejected():
    with pytest.raises(ValueError):
        Bid(HandRank.STRAIGHT, (5,))


def test_five_high_straight_flush_is_rejected():
    with pytest.raises(ValueError):
        Bid(HandRank.STRAIGHT_FLUSH, (Suit.SPADES, 5))


def test_six_high_straight_is_valid():
    bid = Bid(HandRank.STRAIGHT, (6,))
    assert bid.values == (6,)


def test_six_high_straight_flush_is_valid():
    bid = Bid(
        HandRank.STRAIGHT_FLUSH,
        (Suit.HEARTS, 6)
    )

    assert bid.values == (Suit.HEARTS, 6)


def test_royal_flush_requires_suit():
    with pytest.raises(ValueError):
        Bid(HandRank.ROYAL_FLUSH, ())


def test_royal_flush_requires_valid_suit():
    with pytest.raises(TypeError):
        Bid(HandRank.ROYAL_FLUSH, ("Hearts",))


def test_royal_flush_suits_have_equal_strength():
    hearts = Bid(HandRank.ROYAL_FLUSH, (Suit.HEARTS,))
    spades = Bid(HandRank.ROYAL_FLUSH, (Suit.SPADES,))

    assert hearts.strength == spades.strength
    assert not hearts < spades
    assert not spades < hearts


def test_cannot_raise_after_royal_flush():
    manager = BidManager()

    royal = Bid(HandRank.ROYAL_FLUSH, (Suit.HEARTS,))
    manager.place_bid(royal)

    with pytest.raises(ValueError):
        manager.place_bid(
            Bid(HandRank.ROYAL_FLUSH, (Suit.SPADES,))
        )


def test_straight_flush_suits_have_equal_strength():
    hearts = Bid(HandRank.STRAIGHT_FLUSH, (Suit.HEARTS, 9))
    spades = Bid(HandRank.STRAIGHT_FLUSH, (Suit.SPADES, 9))

    assert hearts.strength == spades.strength
    assert not hearts < spades
    assert not spades < hearts


def test_ace_high_straight_flush_is_rejected():
    with pytest.raises(ValueError):
        Bid(HandRank.STRAIGHT_FLUSH, (Suit.HEARTS, 14))
