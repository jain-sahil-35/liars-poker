from game.cards import Card, Rank, Suit
from game.player import Player

from game.terminal_ui import (
    format_card,
    format_cards,
    format_player,
    format_table
)


def test_format_card():

    card = Card(Rank.ACE, Suit.HEARTS)

    assert format_card(card) == "A♥"


def test_format_cards():

    cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.THREE, Suit.CLUBS)
    ]

    assert format_cards(cards) == "A♥  3♣"


def test_format_player_reveals_cards():

    player = Player("p1", "Sahil")

    player.receive_cards([
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.THREE, Suit.CLUBS)
    ])

    result = format_player(player, reveal=True)

    assert "A♥" in result
    assert "3♣" in result


def test_format_player_hides_cards():

    player = Player("p2", "Bot")

    player.receive_cards([
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.SEVEN, Suit.DIAMONDS)
    ])

    result = format_player(player, reveal=False)

    assert "2 cards" in result
    assert "K♠" not in result
    assert "7♦" not in result


def test_eliminated_player_display():

    player = Player("p1", "Sahil")

    player.eliminate()

    assert format_player(player) == "Sahil [ELIMINATED]"


def test_format_table():

    human = Player("p1", "Sahil")
    bot = Player("p2", "Bot")

    human.receive_cards([
        Card(Rank.ACE, Suit.HEARTS)
    ])

    bot.receive_cards([
        Card(Rank.KING, Suit.SPADES)
    ])

    result = format_table([human, bot], "p1")

    assert "A♥" in result
    assert "1 cards" in result
    assert "K♠" not in result
    assert "LIAR'S POKER" in result