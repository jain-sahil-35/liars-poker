
import pytest
from fastapi.testclient import TestClient

from api.main import app, games, game_activity


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_game_storage():
    """Give every test a clean in-memory game store."""

    games.clear()
    game_activity.clear()

    yield

    games.clear()
    game_activity.clear()


def create_test_game():
    """Helper to create a standard four-player game."""

    response = client.post(
        "/games",
        json={
            "player_name": "Test Player",
            "bot_personalities": [
                "Conservative",
                "Aggressive",
                "Detective",
            ],
        },
    )

    assert response.status_code == 200

    return response.json()


# --------------------------------------------------
# BASIC API TESTS
# --------------------------------------------------

def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]


def test_create_game():
    data = create_test_game()

    assert "game_id" in data
    assert data["round_number"] == 1
    assert len(data["players"]) == 4
    assert data["current_player_id"] == "human"
    assert data["current_bid"] is None
    assert data["finished"] is False


def test_create_game_with_different_bot_count():
    response = client.post(
        "/games",
        json={
            "player_name": "Test Player",
            "bot_personalities": ["Conservative"],
        },
    )

    assert response.status_code == 200
    assert len(response.json()["players"]) == 2


def test_game_state_endpoint():
    created_game = create_test_game()
    game_id = created_game["game_id"]

    response = client.get(f"/games/{game_id}")

    assert response.status_code == 200
    assert response.json()["game_id"] == game_id
    assert response.json()["round_number"] == 1


def test_nonexistent_game():
    response = client.get("/games/invalid-game-id")

    assert response.status_code == 404


# --------------------------------------------------
# CARD PRIVACY TESTS
# --------------------------------------------------

def test_opponent_cards_are_hidden():
    data = create_test_game()

    human = data["players"][0]
    bots = data["players"][1:]

    assert len(human["cards"]) == 2

    for bot in bots:
        assert bot["cards"] == []
        assert bot["card_count"] == 2


# --------------------------------------------------
# BIDDING TESTS
# --------------------------------------------------

def test_invalid_bid_category():
    data = create_test_game()
    game_id = data["game_id"]

    response = client.post(
        f"/games/{game_id}/bid",
        json={
            "category": "INVALID_CATEGORY",
            "values": [2],
        },
    )

    assert response.status_code == 400


def test_bid_with_invalid_values():
    data = create_test_game()
    game_id = data["game_id"]

    response = client.post(
        f"/games/{game_id}/bid",
        json={
            "category": "HIGH_CARD",
            "values": [99],
        },
    )

    assert response.status_code == 400


def test_human_can_place_first_bid():
    data = create_test_game()
    game_id = data["game_id"]

    response = client.post(
        f"/games/{game_id}/bid",
        json={
            "category": "HIGH_CARD",
            "values": [2],
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["game_id"] == game_id
    assert result["activity"][0]["player"] == "Test Player"
    assert result["activity"][0]["action"] == "bid"


# --------------------------------------------------
# CHALLENGE TESTS
# --------------------------------------------------

def test_cannot_challenge_before_first_bid():
    data = create_test_game()
    game_id = data["game_id"]

    response = client.post(
        f"/games/{game_id}/challenge"
    )

    assert response.status_code == 400


def test_cannot_start_next_round_before_challenge():
    data = create_test_game()
    game_id = data["game_id"]

    response = client.post(
        f"/games/{game_id}/next-round"
    )

    assert response.status_code == 400


# --------------------------------------------------
# GAME VALIDATION TESTS
# --------------------------------------------------

def test_invalid_game_id_for_bid():
    response = client.post(
        "/games/invalid-game-id/bid",
        json={
            "category": "HIGH_CARD",
            "values": [2],
        },
    )

    assert response.status_code == 404


def test_invalid_game_id_for_challenge():
    response = client.post(
        "/games/invalid-game-id/challenge"
    )

    assert response.status_code == 404
