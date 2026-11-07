import pytest

from game.player import Player
from game.game_state import GameState
from game.bidding import Bid
from game.hand_evaluator import HandRank
from game.cards import Card, Rank, Suit


def make_card(rank, suit):
    return Card(Rank(rank), Suit(suit))


def create_game():

    players = [
        Player("p1", "Sahil"),
        Player("p2", "Bot 1"),
        Player("p3", "Bot 2")
    ]

    return GameState(players)


def test_game_creation():

    game = create_game()

    assert len(game.players) == 3
    assert len(game.active_players) == 3
    assert game.round_number == 0


def test_game_requires_valid_player_count():

    with pytest.raises(ValueError):
        GameState([Player("p1", "Sahil")])


def test_duplicate_player_ids_rejected():

    players = [
        Player("p1", "Sahil"),
        Player("p1", "Bot")
    ]

    with pytest.raises(ValueError):
        GameState(players)


def test_start_game():

    game = create_game()

    game.start_game()

    assert game.started is True
    assert game.round_number == 1

    for player in game.players:
        assert player.card_count == 2


def test_first_player_starts():

    game = create_game()

    game.start_game()

    assert game.current_player.player_id == "p1"


def test_next_turn():

    game = create_game()

    game.start_game()

    game.next_turn()

    assert game.current_player.player_id == "p2"


def test_players_receive_correct_hand_size():

    game = create_game()

    game.players[0].hand_size = 3

    game.start_game()

    assert game.players[0].card_count == 3
    assert game.players[1].card_count == 2


def test_place_bid():

    game = create_game()

    game.start_game()

    bid = Bid(HandRank.ONE_PAIR, (13,))

    game.place_bid("p1", bid)

    assert game.bid_manager.current_bid == bid
    assert game.bidder_id == "p1"


def test_wrong_player_cannot_bid():

    game = create_game()

    game.start_game()

    bid = Bid(HandRank.ONE_PAIR, (13,))

    with pytest.raises(ValueError):
        game.place_bid("p2", bid)


def test_player_rotation_after_previous_loser():

    game = create_game()

    game.start_game()

    game.last_loser_id = "p2"

    game.start_round()

    assert game.current_player.player_id == "p3"


def test_game_cannot_start_twice():

    game = create_game()

    game.start_game()

    with pytest.raises(ValueError):
        game.start_game()


def test_player_lookup():

    game = create_game()

    player = game.get_player("p2")

    assert player.name == "Bot 1"


def test_invalid_player_lookup():

    game = create_game()

    with pytest.raises(ValueError):
        game.get_player("unknown")

def test_cannot_start_next_round_before_challenge():

    game = create_game()
    game.start_game()

    with pytest.raises(ValueError):
        game.start_next_round()


def test_challenge_marks_round_resolved():

    game = create_game()
    game.start_game()

    # Give players known cards.
    game.players[0].cards = [
        make_card(14, Suit.HEARTS),
        make_card(3, Suit.CLUBS)
    ]

    game.players[1].cards = [
        make_card(13, Suit.SPADES),
        make_card(7, Suit.DIAMONDS)
    ]

    game.players[2].cards = [
        make_card(9, Suit.HEARTS),
        make_card(2, Suit.CLUBS)
    ]

    # An impossible Royal Flush claim.
    bid = Bid(HandRank.ROYAL_FLUSH, ())

    game.place_bid("p1", bid)
    game.next_turn()

    result = game.call_bullshit("p2")

    assert result.claim_is_true is False
    assert result.loser_id == "p1"
    assert game.round_resolved is True


def test_next_round_deals_extra_card_to_loser():

    game = create_game()
    game.start_game()

    game.players[0].cards = [
        make_card(14, Suit.HEARTS),
        make_card(3, Suit.CLUBS)
    ]

    game.players[1].cards = [
        make_card(13, Suit.SPADES),
        make_card(7, Suit.DIAMONDS)
    ]

    game.players[2].cards = [
        make_card(9, Suit.HEARTS),
        make_card(2, Suit.CLUBS)
    ]

    bid = Bid(HandRank.ROYAL_FLUSH, ())

    game.place_bid("p1", bid)
    game.next_turn()
    game.call_bullshit("p2")

    game.start_next_round()

    assert game.round_number == 2
    assert game.players[0].card_count == 3
    assert game.players[1].card_count == 2
    assert game.players[2].card_count == 2


def test_next_round_starts_left_of_loser():

    game = create_game()
    game.start_game()

    game.players[0].cards = [
        make_card(14, Suit.HEARTS),
        make_card(3, Suit.CLUBS)
    ]

    game.players[1].cards = [
        make_card(13, Suit.SPADES),
        make_card(7, Suit.DIAMONDS)
    ]

    game.players[2].cards = [
        make_card(9, Suit.HEARTS),
        make_card(2, Suit.CLUBS)
    ]

    bid = Bid(HandRank.ROYAL_FLUSH, ())

    game.place_bid("p1", bid)
    game.next_turn()
    game.call_bullshit("p2")

    game.start_next_round()

    assert game.current_player.player_id == "p2"


def test_round_flag_resets_for_next_round():

    game = create_game()
    game.start_game()

    game.players[0].cards = [
        make_card(14, Suit.HEARTS),
        make_card(3, Suit.CLUBS)
    ]

    game.players[1].cards = [
        make_card(13, Suit.SPADES),
        make_card(7, Suit.DIAMONDS)
    ]

    game.players[2].cards = [
        make_card(9, Suit.HEARTS),
        make_card(2, Suit.CLUBS)
    ]

    bid = Bid(HandRank.ROYAL_FLUSH, ())

    game.place_bid("p1", bid)
    game.next_turn()
    game.call_bullshit("p2")

    game.start_next_round()

    assert game.round_resolved is False
    assert game.bid_manager.current_bid is None
    assert game.bidder_id is None

def test_eliminated_player_is_skipped():

    game = create_game()

    game.players[1].eliminate()

    game.start_game()

    assert game.current_player.player_id == "p1"

    game.next_turn()

    assert game.current_player.player_id == "p3"


def test_losing_with_five_cards_causes_elimination():

    game = create_game()

    game.players[0].hand_size = 5

    game.start_game()

    # Give everyone predictable cards.
    game.players[0].cards = [
        make_card(14, Suit.HEARTS),
        make_card(13, Suit.CLUBS),
        make_card(9, Suit.SPADES),
        make_card(7, Suit.DIAMONDS),
        make_card(3, Suit.HEARTS)
    ]

    game.players[1].cards = [
        make_card(12, Suit.HEARTS),
        make_card(11, Suit.CLUBS)
    ]

    game.players[2].cards = [
        make_card(8, Suit.SPADES),
        make_card(2, Suit.DIAMONDS)
    ]

    bid = Bid(HandRank.ROYAL_FLUSH, ())

    game.place_bid("p1", bid)
    game.next_turn()

    result = game.call_bullshit("p2")

    assert result.loser_id == "p1"
    assert game.players[0].eliminated is True
    assert game.players[0].hand_size == 6
    assert game.players[0].card_count == 0


def test_game_ends_when_only_one_player_remains():

    players = [
        Player("p1", "Sahil", hand_size=5),
        Player("p2", "Bot")
    ]

    game = GameState(players)

    game.start_game()

    game.players[0].cards = [
        make_card(14, Suit.HEARTS),
        make_card(13, Suit.CLUBS),
        make_card(9, Suit.SPADES),
        make_card(7, Suit.DIAMONDS),
        make_card(3, Suit.HEARTS)
    ]

    game.players[1].cards = [
        make_card(12, Suit.HEARTS),
        make_card(11, Suit.CLUBS)
    ]

    bid = Bid(HandRank.ROYAL_FLUSH, ())

    game.place_bid("p1", bid)
    game.next_turn()

    game.call_bullshit("p2")

    assert game.finished is True
    assert game.winner.player_id == "p2"