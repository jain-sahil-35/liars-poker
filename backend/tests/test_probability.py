from game.probability import probability_of_at_least
from math import comb
from game.cards import Card, Rank, Suit
from game.probability import probability_of_rank_claim
import pytest


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