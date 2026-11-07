import pytest

from game.cards import Card, Rank, Suit
from game.bidding import Bid
from game.hand_evaluator import HandRank
from game.claim_verifier import claim_exists
from game.challenge import resolve_challenge


def make_card(rank, suit):
    return Card(Rank(rank), Suit(suit))


def test_pair_of_kings_exists():

    cards = [
        make_card(13, Suit.HEARTS),
        make_card(13, Suit.CLUBS),
        make_card(7, Suit.SPADES)
    ]

    bid = Bid(HandRank.ONE_PAIR, (13,))

    assert claim_exists(cards, bid) is True


def test_pair_of_kings_does_not_exist():

    cards = [
        make_card(13, Suit.HEARTS),
        make_card(12, Suit.CLUBS),
        make_card(7, Suit.SPADES)
    ]

    bid = Bid(HandRank.ONE_PAIR, (13,))

    assert claim_exists(cards, bid) is False


def test_pair_exists_even_if_stronger_hand_exists():

    cards = [
        make_card(13, Suit.HEARTS),
        make_card(13, Suit.CLUBS),
        make_card(13, Suit.SPADES),
        make_card(7, Suit.DIAMONDS),
        make_card(7, Suit.HEARTS)
    ]

    bid = Bid(HandRank.ONE_PAIR, (13,))

    assert claim_exists(cards, bid) is True


def test_three_aces_exist():

    cards = [
        make_card(14, Suit.HEARTS),
        make_card(14, Suit.CLUBS),
        make_card(14, Suit.SPADES),
        make_card(7, Suit.DIAMONDS)
    ]

    bid = Bid(HandRank.THREE_OF_A_KIND, (14,))

    assert claim_exists(cards, bid) is True


def test_wrong_pair_rank():

    cards = [
        make_card(13, Suit.HEARTS),
        make_card(13, Suit.CLUBS),
        make_card(7, Suit.SPADES)
    ]

    bid = Bid(HandRank.ONE_PAIR, (14,))

    assert claim_exists(cards, bid) is False


def test_successful_challenge():

    cards = {
        "player_a": [
            make_card(13, Suit.HEARTS),
            make_card(3, Suit.CLUBS)
        ],

        "player_b": [
            make_card(13, Suit.SPADES),
            make_card(7, Suit.DIAMONDS)
        ]
    }

    bid = Bid(HandRank.ONE_PAIR, (13,))

    result = resolve_challenge(
        cards,
        "player_a",
        "player_b",
        bid
    )

    assert result.claim_is_true is True
    assert result.loser_id == "player_b"


def test_failed_challenge():

    cards = {
        "player_a": [
            make_card(12, Suit.HEARTS),
            make_card(3, Suit.CLUBS)
        ],

        "player_b": [
            make_card(11, Suit.SPADES),
            make_card(7, Suit.DIAMONDS)
        ]
    }

    bid = Bid(HandRank.ONE_PAIR, (14,))

    result = resolve_challenge(
        cards,
        "player_a",
        "player_b",
        bid
    )

    assert result.claim_is_true is False
    assert result.loser_id == "player_a"


def test_bidder_cannot_challenge_themselves():

    cards = {
        "player_a": [
            make_card(13, Suit.HEARTS)
        ]
    }

    bid = Bid(HandRank.ONE_PAIR, (13,))

    with pytest.raises(ValueError):

        resolve_challenge(
            cards,
            "player_a",
            "player_a",
            bid
        )


def test_invalid_bidder():

    cards = {
        "player_b": [
            make_card(13, Suit.HEARTS)
        ]
    }

    bid = Bid(HandRank.ONE_PAIR, (13,))

    with pytest.raises(ValueError):

        resolve_challenge(
            cards,
            "player_a",
            "player_b",
            bid
        )