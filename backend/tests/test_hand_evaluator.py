import pytest

from game.cards import Card, Rank, Suit
from game.hand_evaluator import HandRank, evaluate_hand


def make_card(rank, suit):
    return Card(Rank(rank), Suit(suit))


def test_high_card():
    cards = [
        make_card(14, Suit.HEARTS),
        make_card(11, Suit.CLUBS),
        make_card(9, Suit.SPADES),
        make_card(6, Suit.DIAMONDS),
        make_card(3, Suit.HEARTS)
    ]

    assert evaluate_hand(cards)[0] == HandRank.HIGH_CARD


def test_one_pair():
    cards = [
        make_card(13, Suit.HEARTS),
        make_card(13, Suit.CLUBS),
        make_card(9, Suit.SPADES),
        make_card(6, Suit.DIAMONDS),
        make_card(3, Suit.HEARTS)
    ]

    assert evaluate_hand(cards)[0] == HandRank.ONE_PAIR


def test_two_pair():
    cards = [
        make_card(13, Suit.HEARTS),
        make_card(13, Suit.CLUBS),
        make_card(7, Suit.SPADES),
        make_card(7, Suit.DIAMONDS),
        make_card(3, Suit.HEARTS)
    ]

    assert evaluate_hand(cards)[0] == HandRank.TWO_PAIR


def test_three_of_a_kind():
    cards = [
        make_card(14, Suit.HEARTS),
        make_card(14, Suit.CLUBS),
        make_card(14, Suit.SPADES),
        make_card(6, Suit.DIAMONDS),
        make_card(3, Suit.HEARTS)
    ]

    assert evaluate_hand(cards)[0] == HandRank.THREE_OF_A_KIND


def test_straight():
    cards = [
        make_card(9, Suit.HEARTS),
        make_card(8, Suit.CLUBS),
        make_card(7, Suit.SPADES),
        make_card(6, Suit.DIAMONDS),
        make_card(5, Suit.HEARTS)
    ]

    assert evaluate_hand(cards)[0] == HandRank.STRAIGHT


def test_flush():
    cards = [
        make_card(14, Suit.HEARTS),
        make_card(11, Suit.HEARTS),
        make_card(9, Suit.HEARTS),
        make_card(6, Suit.HEARTS),
        make_card(3, Suit.HEARTS)
    ]

    assert evaluate_hand(cards)[0] == HandRank.FLUSH


def test_full_house():
    cards = [
        make_card(13, Suit.HEARTS),
        make_card(13, Suit.CLUBS),
        make_card(13, Suit.SPADES),
        make_card(7, Suit.DIAMONDS),
        make_card(7, Suit.HEARTS)
    ]

    assert evaluate_hand(cards)[0] == HandRank.FULL_HOUSE


def test_four_of_a_kind():
    cards = [
        make_card(14, Suit.HEARTS),
        make_card(14, Suit.CLUBS),
        make_card(14, Suit.SPADES),
        make_card(14, Suit.DIAMONDS),
        make_card(3, Suit.HEARTS)
    ]

    assert evaluate_hand(cards)[0] == HandRank.FOUR_OF_A_KIND


def test_straight_flush():
    cards = [
        make_card(9, Suit.HEARTS),
        make_card(8, Suit.HEARTS),
        make_card(7, Suit.HEARTS),
        make_card(6, Suit.HEARTS),
        make_card(5, Suit.HEARTS)
    ]

    assert evaluate_hand(cards)[0] == HandRank.STRAIGHT_FLUSH


def test_royal_flush():
    cards = [
        make_card(14, Suit.SPADES),
        make_card(13, Suit.SPADES),
        make_card(12, Suit.SPADES),
        make_card(11, Suit.SPADES),
        make_card(10, Suit.SPADES)
    ]

    assert evaluate_hand(cards)[0] == HandRank.ROYAL_FLUSH


def test_pair_comparison():
    kings = (
        HandRank.ONE_PAIR, 13, 10, 8, 5
    )

    queens = (
        HandRank.ONE_PAIR, 12, 14, 9, 4
    )

    assert kings > queens


def test_best_hand_from_multiple_cards():
    cards = [
        make_card(13, Suit.HEARTS),
        make_card(13, Suit.CLUBS),
        make_card(7, Suit.SPADES),
        make_card(7, Suit.DIAMONDS),
        make_card(3, Suit.HEARTS),
        make_card(14, Suit.CLUBS),
        make_card(2, Suit.SPADES)
    ]

    assert evaluate_hand(cards)[0] == HandRank.TWO_PAIR


def test_empty_hand():
    with pytest.raises(ValueError):
        evaluate_hand([])


def test_four_card_two_pair():
    cards = [
        make_card(13, Suit.HEARTS),
        make_card(13, Suit.CLUBS),
        make_card(7, Suit.SPADES),
        make_card(7, Suit.DIAMONDS)
    ]

    assert evaluate_hand(cards)[0] == HandRank.TWO_PAIR


def test_ace_low_sequence_is_not_a_straight():
    cards = [
        make_card(14, Suit.HEARTS),
        make_card(2, Suit.CLUBS),
        make_card(3, Suit.SPADES),
        make_card(4, Suit.DIAMONDS),
        make_card(5, Suit.HEARTS)
    ]

    assert evaluate_hand(cards)[0] == HandRank.HIGH_CARD


def test_ace_low_sequence_is_not_a_straight_flush():
    cards = [
        make_card(14, Suit.HEARTS),
        make_card(2, Suit.HEARTS),
        make_card(3, Suit.HEARTS),
        make_card(4, Suit.HEARTS),
        make_card(5, Suit.HEARTS)
    ]

    assert evaluate_hand(cards)[0] == HandRank.FLUSH
