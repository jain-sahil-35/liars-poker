import pytest

from game.opponent_manager import OpponentProfileManager


def test_manager_creates_profiles_for_all_players():
    manager = OpponentProfileManager(["p1", "p2", "p3"])

    assert len(manager.profiles) == 3


def test_get_profile():
    manager = OpponentProfileManager(["p1", "p2"])

    profile = manager.get_profile("p1")

    assert profile.player_id == "p1"


def test_get_unknown_player_raises_error():
    manager = OpponentProfileManager(["p1"])

    with pytest.raises(KeyError):
        manager.get_profile("unknown")


def test_record_bid():
    manager = OpponentProfileManager(["p1"])

    manager.record_bid("p1")
    manager.record_bid("p1")

    assert manager.get_profile("p1").total_bids == 2


def test_record_claim():
    manager = OpponentProfileManager(["p1"])

    manager.record_claim("p1", False)
    manager.record_claim("p1", True)

    profile = manager.get_profile("p1")

    assert profile.false_claims == 1
    assert profile.true_claims == 1


def test_record_challenge():
    manager = OpponentProfileManager(["p1"])

    manager.record_challenge("p1", True)
    manager.record_challenge("p1", False)

    profile = manager.get_profile("p1")

    assert profile.challenges_won == 1
    assert profile.challenges_lost == 1


def test_player_profiles_are_independent():
    manager = OpponentProfileManager(["p1", "p2"])

    manager.record_bid("p1")

    assert manager.get_profile("p1").total_bids == 1
    assert manager.get_profile("p2").total_bids == 0


def test_reset_clears_all_profiles():
    manager = OpponentProfileManager(["p1", "p2"])

    manager.record_bid("p1")
    manager.record_claim("p2", False)
    manager.record_challenge("p1", False)

    manager.reset()

    assert manager.get_profile("p1").total_bids == 0
    assert manager.get_profile("p1").challenges_lost == 0
    assert manager.get_profile("p2").false_claims == 0


def test_reset_preserves_player_profiles():
    manager = OpponentProfileManager(["p1", "p2"])

    manager.reset()

    assert len(manager.profiles) == 2
    assert manager.get_profile("p1").player_id == "p1"