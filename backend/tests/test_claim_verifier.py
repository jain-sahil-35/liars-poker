
import pytest

from game.cards import Card, Rank, Suit
from game.bidding import Bid
from game.hand_evaluator import HandRank
from game.claim_verifier import claim_exists


def make_card(rank, suit):
    return Card(Rank(rank), Suit(suit))


def test_high_card_claim():
    cards = [make_card(14, Suit.HEARTS)]

    bid = Bid(HandRank.HIGH_CARD, (14,))

    assert claim_exists(cards, bid) is True


def test_one_pair_claim():
    cards = [
        make_card(14, Suit.HEARTS),
        make_card(14, Suit.CLUBS)
    ]

    bid = Bid(HandRank.ONE_PAIR, (14,))

    assert claim_exists(cards, bid) is True


def test_two_pair_claim():
    cards = [
        make_card(14, Suit.HEARTS),
        make_card(14, Suit.CLUBS),
        make_card(10, Suit.SPADES),
        make_card(10, Suit.DIAMONDS)
    ]

    bid = Bid(HandRank.TWO_PAIR, (14, 10))

    assert claim_exists(cards, bid) is True


def test_three_of_a_kind_claim():
    cards = [
        make_card(13, Suit.HEARTS),
        make_card(13, Suit.CLUBS),
        make_card(13, Suit.SPADES)
    ]

    bid = Bid(HandRank.THREE_OF_A_KIND, (13,))

    assert claim_exists(cards, bid) is True


def test_straight_claim():
    cards = [
        make_card(10, Suit.HEARTS),
        make_card(9, Suit.CLUBS),
        make_card(8, Suit.SPADES),
        make_card(7, Suit.DIAMONDS),
        make_card(6, Suit.HEARTS)
    ]

    bid = Bid(HandRank.STRAIGHT, (10,))

    assert claim_exists(cards, bid) is True


def test_flush_claim():
    cards = [
        make_card(14, Suit.HEARTS),
        make_card(12, Suit.HEARTS),
        make_card(10, Suit.HEARTS),
        make_card(8, Suit.HEARTS),
        make_card(5, Suit.HEARTS)
    ]

    bid = Bid(HandRank.FLUSH, (14, 12, 10, 8, 5))

    assert claim_exists(cards, bid) is True


def test_full_house_claim():
    cards = [
        make_card(7, Suit.HEARTS),
        make_card(7, Suit.CLUBS),
        make_card(7, Suit.SPADES),
        make_card(14, Suit.DIAMONDS),
        make_card(14, Suit.HEARTS)
    ]

    bid = Bid(HandRank.FULL_HOUSE, (7, 14))

    assert claim_exists(cards, bid) is True


def test_four_of_a_kind_claim():
    cards = [
        make_card(14, Suit.HEARTS),
        make_card(14, Suit.CLUBS),
        make_card(14, Suit.SPADES),
        make_card(14, Suit.DIAMONDS)
    ]

    bid = Bid(HandRank.FOUR_OF_A_KIND, (14,))

    assert claim_exists(cards, bid) is True


def test_straight_flush_claim():
    cards = [
        make_card(9, Suit.HEARTS),
        make_card(8, Suit.HEARTS),
        make_card(7, Suit.HEARTS),
        make_card(6, Suit.HEARTS),
        make_card(5, Suit.HEARTS)
    ]

    bid = Bid(HandRank.STRAIGHT_FLUSH, (9,))

    assert claim_exists(cards, bid) is True


def test_royal_flush_claim():
    cards = [
        make_card(14, Suit.SPADES),
        make_card(13, Suit.SPADES),
        make_card(12, Suit.SPADES),
        make_card(11, Suit.SPADES),
        make_card(10, Suit.SPADES)
    ]

    bid = Bid(HandRank.ROYAL_FLUSH, ())

    assert claim_exists(cards, bid) is True


def test_false_pair_claim():
    cards = [
        make_card(14, Suit.HEARTS),
        make_card(13, Suit.CLUBS)
    ]

    bid = Bid(HandRank.ONE_PAIR, (14,))

    assert claim_exists(cards, bid) is False


def test_claim_fails_when_not_enough_cards():
    cards = [make_card(14, Suit.HEARTS)]

    bid = Bid(HandRank.ONE_PAIR, (14,))

    assert claim_exists(cards, bid) is False
