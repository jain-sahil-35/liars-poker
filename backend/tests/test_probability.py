from game.probability import probability_of_at_least
from math import comb
from game.cards import Card, Rank, Suit
from game.probability import probability_of_rank_claim
import pytest
from game.probability import probability_of_claim
import random
from game.bidding import Bid
from game.hand_evaluator import HandRank
from game.probability import _claim_exists_fast
from game.claim_verifier import claim_exists


def test_probability_when_no_successes_are_required():
    result = probability_of_at_least(0, 3, 10, 50)
    assert result == 1.0


def test_probability_when_not_enough_successes_exist():
    result = probability_of_at_least(4, 3, 10, 50)
    assert result == 0.0


def test_probability_when_no_successes_are_available():
    result = probability_of_at_least(1, 0, 10, 50)
    assert result == 0.0


def test_probability_of_at_least_one_success():
    result = probability_of_at_least(1, 3, 10, 50)

    expected = 1 - (comb(47, 10) / comb(50, 10))

    assert abs(result - expected) < 1e-9


def test_probability_of_at_least_two_successes():
    result = probability_of_at_least(2, 3, 10, 50)

    expected = sum(
        comb(3, k) * comb(47, 10 - k) / comb(50, 10)
        for k in range(2, 4)
    )

    assert abs(result - expected) < 1e-9

def test_rank_claim_with_enough_known_cards():
    cards = [
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.KING, Suit.CLUBS),
    ]

    result = probability_of_rank_claim(
        cards, 12, Rank.KING, 3
    )

    assert result == 1.0


def test_rank_claim_with_one_known_card():
    cards = [
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.TWO, Suit.SPADES),
    ]

    result = probability_of_rank_claim(
        cards, 12, Rank.KING, 3
    )

    expected = probability_of_at_least(2, 3, 10, 50)

    assert abs(result - expected) < 1e-9


def test_rank_claim_with_no_known_cards():
    cards = [
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.SPADES),
    ]

    result = probability_of_rank_claim(
        cards, 12, Rank.KING, 2
    )

    expected = probability_of_at_least(2, 4, 10, 50)

    assert abs(result - expected) < 1e-9


def test_rank_claim_when_no_more_cards_are_needed():
    cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.ACE, Suit.SPADES),
    ]

    result = probability_of_rank_claim(
        cards, 12, Rank.ACE, 2
    )

    assert result == 1.0


def test_rank_claim_when_too_many_cards_are_required():
    cards = [
        Card(Rank.KING, Suit.HEARTS),
    ]

    with pytest.raises(ValueError):
        probability_of_rank_claim(
            cards, 12, Rank.KING, 5
        )

def test_rejects_negative_total_cards():
    with pytest.raises(ValueError):
        probability_of_rank_claim([], -1, Rank.KING, 2)


def test_rejects_more_than_52_cards():
    with pytest.raises(ValueError):
        probability_of_rank_claim([], 53, Rank.KING, 2)


def test_rejects_player_holding_more_cards_than_total():
    cards = [
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.ACE, Suit.SPADES),
    ]

    with pytest.raises(ValueError):
        probability_of_rank_claim(cards, 1, Rank.KING, 2)


def test_rejects_invalid_required_count():
    with pytest.raises(ValueError):
        probability_of_rank_claim([], 10, Rank.KING, 5)


def test_rejects_zero_required_count():
    with pytest.raises(ValueError):
        probability_of_rank_claim([], 10, Rank.KING, 0)


def test_rejects_non_card_objects():
    with pytest.raises(TypeError):
        probability_of_rank_claim(["King"], 10, Rank.KING, 2)


def test_probability_of_guaranteed_pair():
    cards = [
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.KING, Suit.SPADES)
    ]

    bid = Bid(HandRank.ONE_PAIR, (13,))

    assert probability_of_claim(cards, 6, bid) == 1.0


def test_probability_of_impossible_claim():
    cards = [
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.SPADES)
    ]

    bid = Bid(HandRank.ROYAL_FLUSH, (Suit.HEARTS,))

    assert probability_of_claim(cards, 4, bid) == 0.0


def test_probability_of_guaranteed_royal_flush():
    cards = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.QUEEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.TEN, Suit.SPADES)
    ]

    bid = Bid(HandRank.ROYAL_FLUSH, (Suit.SPADES,))

    assert probability_of_claim(cards, 5, bid) == 1.0


def test_probability_of_flush_is_reproducible():
    cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.TWO, Suit.CLUBS)
    ]

    bid = Bid(HandRank.FLUSH, (Suit.HEARTS, Rank.ACE))

    first = probability_of_claim(
        cards, 8, bid, simulations=1000,
        rng=random.Random(42)
    )

    second = probability_of_claim(
        cards, 8, bid, simulations=1000,
        rng=random.Random(42)
    )

    assert first == second


def test_probability_rejects_invalid_simulation_count():
    bid = Bid(HandRank.FLUSH, (Suit.HEARTS, Rank.ACE))

    with pytest.raises(ValueError):
        probability_of_claim([], 8, bid, simulations=0)


def test_probability_of_guaranteed_two_pair():
    cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.KING, Suit.CLUBS)
    ]

    bid = Bid(HandRank.TWO_PAIR, (14, 13))

    assert probability_of_claim(cards, 4, bid) == 1.0


def test_probability_of_guaranteed_straight():
    cards = [
        Card(Rank.SIX, Suit.HEARTS),
        Card(Rank.SEVEN, Suit.CLUBS),
        Card(Rank.EIGHT, Suit.SPADES),
        Card(Rank.NINE, Suit.DIAMONDS),
        Card(Rank.TEN, Suit.HEARTS)
    ]

    bid = Bid(HandRank.STRAIGHT, (10,))

    assert probability_of_claim(cards, 5, bid) == 1.0


def test_probability_of_guaranteed_full_house():
    cards = [
        Card(Rank.SEVEN, Suit.HEARTS),
        Card(Rank.SEVEN, Suit.CLUBS),
        Card(Rank.SEVEN, Suit.SPADES),
        Card(Rank.ACE, Suit.DIAMONDS),
        Card(Rank.ACE, Suit.HEARTS)
    ]

    bid = Bid(HandRank.FULL_HOUSE, (7, 14))

    assert probability_of_claim(cards, 5, bid) == 1.0


def test_probability_of_guaranteed_straight_flush():
    cards = [
        Card(Rank.NINE, Suit.HEARTS),
        Card(Rank.EIGHT, Suit.HEARTS),
        Card(Rank.SEVEN, Suit.HEARTS),
        Card(Rank.SIX, Suit.HEARTS),
        Card(Rank.FIVE, Suit.HEARTS)
    ]

    bid = Bid(HandRank.STRAIGHT_FLUSH, (9,))

    assert probability_of_claim(cards, 5, bid) == 1.0

def test_fast_claim_checker_matches_original_verifier():
    cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.KING, Suit.CLUBS),
        Card(Rank.QUEEN, Suit.HEARTS),
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.TEN, Suit.HEARTS),
    ]

    bids = [
        Bid(HandRank.HIGH_CARD, (14,)),
        Bid(HandRank.ONE_PAIR, (14,)),
        Bid(HandRank.TWO_PAIR, (14, 13)),
        Bid(HandRank.THREE_OF_A_KIND, (14,)),
        Bid(HandRank.STRAIGHT, (14,)),
        Bid(HandRank.FLUSH, (Suit.HEARTS, Rank.QUEEN)),
        Bid(HandRank.FULL_HOUSE, (14, 13)),
        Bid(HandRank.FOUR_OF_A_KIND, (14,)),
        Bid(HandRank.STRAIGHT_FLUSH, (14,)),
        Bid(HandRank.ROYAL_FLUSH, (Suit.HEARTS,))
    ]

    for bid in bids:
        assert _claim_exists_fast(cards, bid) == claim_exists(cards, bid)


def test_fast_checker_matches_original_on_random_card_sets():
    rng = random.Random(42)

    deck = [
        Card(rank, suit)
        for rank in Rank
        for suit in Suit
    ]

    bids = [
        Bid(HandRank.HIGH_CARD, (14,)),
        Bid(HandRank.ONE_PAIR, (13,)),
        Bid(HandRank.TWO_PAIR, (14, 10)),
        Bid(HandRank.THREE_OF_A_KIND, (12,)),
        Bid(HandRank.STRAIGHT, (10,)),
        Bid(HandRank.FLUSH, (Suit.HEARTS, Rank.QUEEN)),
        Bid(HandRank.FULL_HOUSE, (7, 14)),
        Bid(HandRank.FOUR_OF_A_KIND, (11,)),
        Bid(HandRank.STRAIGHT_FLUSH, (9,)),
        Bid(HandRank.ROYAL_FLUSH, (Suit.HEARTS,))
    ]

    for _ in range(200):
        cards = rng.sample(deck, rng.randint(5, 10))

        for bid in bids:
            fast_result = _claim_exists_fast(cards, bid)
            original_result = claim_exists(cards, bid)

            assert fast_result == original_result, (
                f"Mismatch for {bid} with cards {cards}"
            )


def test_fast_checker_uses_new_flush_rules():
    cards = [
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.HEARTS),
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.NINE, Suit.HEARTS),
        Card(Rank.SEVEN, Suit.HEARTS),
        Card(Rank.FOUR, Suit.HEARTS),
    ]

    bid = Bid(HandRank.FLUSH, (Suit.HEARTS, Rank.QUEEN))

    assert _claim_exists_fast(cards, bid) is True
    assert _claim_exists_fast(cards, bid) == claim_exists(cards, bid)


def test_fast_checker_rejects_ace_low_straight():
    cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.TWO, Suit.CLUBS),
        Card(Rank.THREE, Suit.SPADES),
        Card(Rank.FOUR, Suit.DIAMONDS),
        Card(Rank.FIVE, Suit.HEARTS),
    ]

    bid = Bid(HandRank.STRAIGHT, (6,))

    assert _claim_exists_fast(cards, bid) is False
    assert _claim_exists_fast(cards, bid) == claim_exists(cards, bid)


def test_royal_flush_requires_the_claimed_suit():
    cards = [
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.QUEEN, Suit.SPADES),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.ACE, Suit.SPADES),
    ]

    hearts_bid = Bid(
        HandRank.ROYAL_FLUSH,
        (Suit.HEARTS,)
    )

    spades_bid = Bid(
        HandRank.ROYAL_FLUSH,
        (Suit.SPADES,)
    )

    assert _claim_exists_fast(cards, hearts_bid) is False
    assert _claim_exists_fast(cards, spades_bid) is True


def test_original_verifier_checks_royal_flush_suit():
    cards = [
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.QUEEN, Suit.SPADES),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.ACE, Suit.SPADES),
    ]

    hearts_bid = Bid(
        HandRank.ROYAL_FLUSH,
        (Suit.HEARTS,)
    )

    assert claim_exists(cards, hearts_bid) is False


def test_probability_rejects_royal_flush_in_wrong_suit():
    cards = [
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.QUEEN, Suit.SPADES),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.ACE, Suit.SPADES),
    ]

    hearts_bid = Bid(
        HandRank.ROYAL_FLUSH,
        (Suit.HEARTS,)
    )

    assert probability_of_claim(cards, 5, hearts_bid) == 0.0
