import pytest

from game.deck import Deck
from game.cards import Card


def test_deck_has_52_cards():
    deck = Deck()

    assert deck.remaining == 52


def test_deck_has_unique_cards():
    deck = Deck()

    assert len(set(deck.cards)) == 52


def test_draw_card():
    deck = Deck()

    card = deck.draw()

    assert isinstance(card, Card)
    assert deck.remaining == 51


def test_deal_multiple_cards():
    deck = Deck()

    hand = deck.deal(5)

    assert len(hand) == 5
    assert deck.remaining == 47


def test_cannot_draw_from_empty_deck():
    deck = Deck()

    deck.deal(52)

    with pytest.raises(ValueError):
        deck.draw()


def test_cannot_deal_more_cards_than_available():
    deck = Deck()

    with pytest.raises(ValueError):
        deck.deal(53)


def test_negative_deal():
    deck = Deck()

    with pytest.raises(ValueError):
        deck.deal(-1)


def test_reset_deck():
    deck = Deck()

    deck.deal(10)
    deck.reset()

    assert deck.remaining == 52
    assert len(set(deck.cards)) == 52