from game.opponent_profile import OpponentProfile


def test_profile_starts_with_zero_statistics():
    profile = OpponentProfile("player1")

    assert profile.player_id == "player1"
    assert profile.total_bids == 0
    assert profile.false_claims == 0
    assert profile.true_claims == 0
    assert profile.challenges_won == 0
    assert profile.challenges_lost == 0


def test_record_bid():
    profile = OpponentProfile("player1")

    profile.record_bid()
    profile.record_bid()

    assert profile.total_bids == 2


def test_record_false_claim():
    profile = OpponentProfile("player1")

    profile.record_claim(False)

    assert profile.false_claims == 1


def test_record_true_claim():
    profile = OpponentProfile("player1")

    profile.record_claim(True)

    assert profile.true_claims == 1


def test_false_claim_rate():
    profile = OpponentProfile("player1")

    profile.record_claim(False)
    profile.record_claim(False)
    profile.record_claim(False)
    profile.record_claim(True)

    assert abs(profile.false_claim_rate - (4 / 6)) < 1e-9


def test_false_claim_rate_without_observations():
    profile = OpponentProfile("player1")

    assert profile.false_claim_rate == 0.5


def test_record_successful_challenge():
    profile = OpponentProfile("player1")

    profile.record_challenge(True)

    assert profile.challenges_won == 1


def test_record_failed_challenge():
    profile = OpponentProfile("player1")

    profile.record_challenge(False)

    assert profile.challenges_lost == 1


def test_challenge_success_rate():
    profile = OpponentProfile("player1")

    profile.record_challenge(True)
    profile.record_challenge(True)
    profile.record_challenge(False)

    assert abs(profile.challenge_success_rate - (2 / 3)) < 1e-9


def test_challenge_success_rate_without_observations():
    profile = OpponentProfile("player1")

    assert profile.challenge_success_rate == 0.0


def test_reset_profile():
    profile = OpponentProfile("player1")

    profile.record_bid()
    profile.record_claim(False)
    profile.record_challenge(False)

    profile.reset()

    assert profile.total_bids == 0
    assert profile.false_claims == 0
    assert profile.true_claims == 0
    assert profile.challenges_won == 0
    assert profile.challenges_lost == 0