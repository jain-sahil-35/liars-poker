import pytest

from game.player import Player
from game.cards import Card, Rank, Suit


def make_card(rank):
    return Card(Rank(rank), Suit.HEARTS)


def test_player_creation():

    player = Player("p1", "Sahil")

    assert player.player_id == "p1"
    assert player.name == "Sahil"
    assert player.card_count == 0
    assert player.eliminated is False


def test_receive_cards():

    player = Player("p1", "Sahil")

    cards = [
        make_card(14),
        make_card(13)
    ]

    player.receive_cards(cards)

    assert player.card_count == 2


def test_players_have_independent_hands():

    player1 = Player("p1", "Sahil")
    player2 = Player("p2", "Bot")

    player1.receive_cards([make_card(14)])

    assert player1.card_count == 1
    assert player2.card_count == 0


def test_clear_cards():

    player = Player("p1", "Sahil")

    player.receive_cards([
        make_card(14),
        make_card(13)
    ])

    player.clear_cards()

    assert player.card_count == 0


def test_eliminate_player():

    player = Player("p1", "Sahil")

    player.receive_cards([
        make_card(14),
        make_card(13)
    ])

    player.eliminate()

    assert player.eliminated is True
    assert player.card_count == 0


def test_eliminated_player_cannot_receive_cards():

    player = Player("p1", "Sahil")

    player.eliminate()

    with pytest.raises(ValueError):
        player.receive_cards([make_card(14)])

def test_penalty_increases_hand_size():

    player = Player("p1", "Sahil")

    player.add_penalty_card()

    assert player.hand_size == 3


def test_player_eliminated_at_six_cards():

    player = Player("p1", "Sahil")
    player.hand_size = 5

    player.add_penalty_card()

    assert player.eliminated is True
    assert player.hand_size == 6
    assert player.card_count == 0


def test_player_not_eliminated_before_six():

    player = Player("p1", "Sahil")
    player.hand_size = 4

    player.add_penalty_card()

    assert player.eliminated is False
    assert player.hand_size == 5


def test_eliminated_player_cannot_receive_penalty():

    player = Player("p1", "Sahil")

    player.eliminate()

    with pytest.raises(ValueError):
        player.add_penalty_card()