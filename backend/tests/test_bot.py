from game.bot import Bot, BotPersonality
from game.player import Player
from game.bidding import Bid
from game.hand_evaluator import HandRank
from game.cards import Card, Rank, Suit
from game.opponent_manager import OpponentProfileManager
from game.bid_history import BidHistory
from game.opponent_profile import OpponentProfile

def create_bot(personality):

    player = Player("bot1", "Test Bot")

    return Bot(player, personality)


def test_bot_creation():

    bot = create_bot(BotPersonality.CONSERVATIVE)

    assert bot.name == "Test Bot"
    assert bot.player_id == "bot1"


def test_bot_personality():

    bot = create_bot(BotPersonality.AGGRESSIVE)

    assert bot.personality == BotPersonality.AGGRESSIVE


def test_bot_makes_first_bid(monkeypatch):
    bot = create_bot(BotPersonality.CONSERVATIVE)

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args, **kwargs: 0.90
    )

    bid = bot.choose_bid(None, total_cards=6)

    assert isinstance(bid, Bid)
    assert bot.last_bid_probability == 0.90


def test_bot_raises_current_bid(monkeypatch):
    bot = create_bot(BotPersonality.CONSERVATIVE)

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args, **kwargs: 0.90
    )

    current_bid = Bid(HandRank.ONE_PAIR, (10,))
    new_bid = bot.choose_bid(current_bid, total_cards=6)

    assert new_bid > current_bid


def test_conservative_bot_chooses_confident_raise(monkeypatch):
    bot = create_bot(BotPersonality.CONSERVATIVE)

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args, **kwargs: 0.90
    )

    current_bid = Bid(HandRank.ONE_PAIR, (10,))
    new_bid = bot.choose_bid(current_bid, total_cards=6)

    assert new_bid > current_bid
    assert bot.last_bid_probability >= 0.75


def test_aggressive_bot_chooses_higher_bid(monkeypatch):
    bot = create_bot(BotPersonality.AGGRESSIVE)

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args, **kwargs: 0.50
    )

    current_bid = Bid(HandRank.ONE_PAIR, (10,))
    new_bid = bot.choose_bid(current_bid, total_cards=6)

    assert new_bid > current_bid
    assert bot.last_bid_probability >= 0.35


def test_bot_decision_format(monkeypatch):
    bot = create_bot(BotPersonality.CONSERVATIVE)

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args, **kwargs: 0.90
    )

    action, bid = bot.decide_action(None, 6)

    assert action == "bid"
    assert isinstance(bid, Bid)


def test_bot_statistics():

    bot = create_bot(BotPersonality.DETECTIVE)

    assert bot.total_bids == 0
    assert bot.successful_challenges == 0
    assert bot.failed_challenges == 0

def test_conservative_bot_accepts_low_probability_claim():
    player = Player("1", "Bot", cards=[
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.SPADES)
    ])

    bot = Bot(player, BotPersonality.CONSERVATIVE)
    bid = Bid(HandRank.FOUR_OF_A_KIND, (14,))

    assert bot.should_challenge(bid, 12) is True

def test_aggressive_bot_challenges_more_readily():
    player = Player("1", "Bot", cards=[
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.SPADES)
    ])

    bot = Bot(player, BotPersonality.AGGRESSIVE)
    bid = Bid(HandRank.THREE_OF_A_KIND, (14,))

    assert bot.should_challenge(bid, 12) is True

def test_conservative_bot_challenges_very_unlikely_claim():
    player = Player("1", "Bot", cards=[
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.KING, Suit.SPADES)
    ])

    bot = Bot(player, BotPersonality.AGGRESSIVE)
    bid = Bid(HandRank.ONE_PAIR, (13,))

    assert bot.should_challenge(bid, 12) is False

def test_detective_learns_from_false_claims(monkeypatch):

    player = Player("bot", "Detective")

    manager = OpponentProfileManager(["bot", "alice"])

    detective = Bot(
        player,
        BotPersonality.DETECTIVE,
        manager
    )

    bid = Bid(HandRank.THREE_OF_A_KIND, (14,))

    # Keep the probability fixed so this test isolates
    # the effect of opponent history.
    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args: 0.30
    )

    # Initially, the Detective should not challenge.
    assert detective.should_challenge(bid, 12, "alice") is False

    # Alice makes four false claims.
    for _ in range(4):
        manager.record_claim("alice", False)

    # The Detective should now be more suspicious.
    assert detective.should_challenge(bid, 12, "alice") is True


def test_detective_does_not_adjust_for_own_claim_history(monkeypatch):

    player = Player("bot", "Detective")

    manager = OpponentProfileManager(["bot", "alice"])

    detective = Bot(
        player,
        BotPersonality.DETECTIVE,
        manager
    )

    bid = Bid(HandRank.THREE_OF_A_KIND, (14,))

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args: 0.30
    )

    for _ in range(4):
        manager.record_claim("bot", False)

    # The bot must not use its own claim history
    # when evaluating its own bid.
    assert detective.should_challenge(bid, 12, "bot") is False


def test_detective_works_without_opponent_manager(monkeypatch):

    player = Player("bot", "Detective")

    detective = Bot(player, BotPersonality.DETECTIVE)

    bid = Bid(HandRank.THREE_OF_A_KIND, (14,))

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args: 0.30
    )

    assert detective.should_challenge(bid, 12, "alice") is False


def test_bot_generates_all_ten_categories():
    bot = create_bot(BotPersonality.CONSERVATIVE)

    candidates = bot.generate_candidates()

    categories = {bid.category for bid in candidates}

    assert categories == set(HandRank)


def test_all_generated_bids_are_structurally_valid():
    bot = create_bot(BotPersonality.CONSERVATIVE)

    candidates = bot.generate_candidates()

    assert len(candidates) == 383

    for bid in candidates:
        assert isinstance(bid, Bid)
        assert bid.category in HandRank


def test_bot_generates_flush_bids_for_all_suits_and_ranks():
    bot = create_bot(BotPersonality.CONSERVATIVE)

    flush_bids = [
        bid for bid in bot.generate_candidates()
        if bid.category == HandRank.FLUSH
    ]

    assert len(flush_bids) == 52

    assert {
        bid.values[0] for bid in flush_bids
    } == set(Suit)

    assert {
        bid.values[1] for bid in flush_bids
    } == set(Rank)



def test_bot_can_raise_to_two_pair(monkeypatch):

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args, **kwargs: 0.90
    )

    bot = create_bot(BotPersonality.CONSERVATIVE)

    current_bid = Bid(HandRank.ONE_PAIR, (14,))
    new_bid = bot.choose_bid(current_bid)

    assert new_bid > current_bid


def test_bot_can_raise_to_flush(monkeypatch):

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args, **kwargs: 0.90
    )

    bot = create_bot(BotPersonality.CONSERVATIVE)

    current_bid = Bid(HandRank.FULL_HOUSE, (14, 13))
    new_bid = bot.choose_bid(current_bid)

    assert new_bid > current_bid


def test_bot_returns_none_when_no_higher_bid_exists():
    bot = create_bot(BotPersonality.CONSERVATIVE)

    current_bid = Bid(HandRank.ROYAL_FLUSH, (Suit.HEARTS,))

    assert bot.choose_bid(current_bid) is None


def test_bot_generates_valid_full_house_claims():
    bot = create_bot(BotPersonality.CONSERVATIVE)

    candidates = [
        bid for bid in bot.generate_candidates()
        if bid.category == HandRank.FULL_HOUSE
    ]

    assert len(candidates) == 13 * 12

    for bid in candidates:
        assert bid.values[0] != bid.values[1]


def test_bot_can_challenge_complex_claims(monkeypatch):
    player = Player("bot1", "Test Bot")
    bot = Bot(player, BotPersonality.AGGRESSIVE)

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args: 0.10
    )

    bids = [
        Bid(HandRank.HIGH_CARD, (14,)),
        Bid(HandRank.ONE_PAIR, (14,)),
        Bid(HandRank.TWO_PAIR, (14, 10)),
        Bid(HandRank.THREE_OF_A_KIND, (14,)),
        Bid(HandRank.STRAIGHT, (10,)),
        Bid(HandRank.FLUSH, (Suit.HEARTS, Rank.QUEEN)),
        Bid(HandRank.FULL_HOUSE, (14, 10)),
        Bid(HandRank.FOUR_OF_A_KIND, (14,)),
        Bid(HandRank.STRAIGHT_FLUSH, (Suit.SPADES, 9)),
        Bid(HandRank.ROYAL_FLUSH, (Suit.HEARTS,))
    ]

    for bid in bids:
        assert bot.should_challenge(bid, 12) is True


def test_conservative_bot_requires_lower_probability(monkeypatch):
    bot = create_bot(BotPersonality.CONSERVATIVE)

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args: 0.20
    )

    bid = Bid(HandRank.FLUSH, (Suit.HEARTS, Rank.QUEEN))

    assert bot.should_challenge(bid, 12) is False


def test_aggressive_bot_challenges_at_higher_probability(monkeypatch):
    bot = create_bot(BotPersonality.AGGRESSIVE)

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args: 0.30
    )

    bid = Bid(HandRank.FLUSH, (Suit.HEARTS, Rank.QUEEN))

    assert bot.should_challenge(bid, 12) is True


def test_detective_adjusts_complex_claim_suspicion(monkeypatch):
    player = Player("bot", "Detective")
    manager = OpponentProfileManager(["bot", "alice"])

    detective = Bot(
        player,
        BotPersonality.DETECTIVE,
        manager
    )

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args: 0.30
    )

    bid = Bid(HandRank.STRAIGHT, (10,))

    # Initially, 30% probability is above the Detective's 25% threshold.
    assert detective.should_challenge(bid, 12, "alice") is False

    # Alice makes four false claims.
    for _ in range(4):
        manager.record_claim("alice", False)

    # Historical behaviour increases suspicion.
    assert detective.should_challenge(bid, 12, "alice") is True

def test_bot_uses_own_cards_to_rank_candidates():
    player = Player(
        "bot1",
        "Test Bot",
        cards=[
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.KING, Suit.SPADES),
        ]
    )

    bot = Bot(player, BotPersonality.CONSERVATIVE)

    pair_of_kings = Bid(HandRank.ONE_PAIR, (13,))
    pair_of_queens = Bid(HandRank.ONE_PAIR, (12,))

    assert bot._card_support(pair_of_kings) > bot._card_support(pair_of_queens)


def test_bot_uses_suit_for_flush_support():
    player = Player(
        "bot1",
        "Test Bot",
        cards=[
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.HEARTS),
        ]
    )

    bot = Bot(player, BotPersonality.CONSERVATIVE)

    hearts_flush = Bid(
        HandRank.FLUSH,
        (Suit.HEARTS, Rank.QUEEN)
    )

    spades_flush = Bid(
        HandRank.FLUSH,
        (Suit.SPADES, Rank.QUEEN)
    )

    assert bot._card_support(hearts_flush) > bot._card_support(spades_flush)


def test_bot_records_probability_of_selected_bid(monkeypatch):
    bot = create_bot(BotPersonality.DETECTIVE)

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args, **kwargs: 0.80
    )

    bot.choose_bid(None, total_cards=6)

    assert bot.last_bid_probability == 0.80


def test_opponent_profile_tracks_bid_categories():
    manager = OpponentProfileManager(["alice"])

    bid1 = Bid(HandRank.ONE_PAIR, (10,))
    bid2 = Bid(HandRank.TWO_PAIR, (10, 8))
    bid3 = Bid(HandRank.ONE_PAIR, (12,))

    manager.record_bid("alice", bid1)
    manager.record_bid("alice", bid2)
    manager.record_bid("alice", bid3)

    profile = manager.get_profile("alice")

    assert profile.total_bids == 3
    assert profile.category_frequency(HandRank.ONE_PAIR) == 2 / 3
    assert profile.category_frequency(HandRank.TWO_PAIR) == 1 / 3


def test_detective_uses_repeated_bid_patterns(monkeypatch):
    player = Player("bot", "Detective")
    manager = OpponentProfileManager(["bot", "alice"])

    detective = Bot(
        player,
        BotPersonality.DETECTIVE,
        manager
    )

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args, **kwargs: 0.29
    )

    history = BidHistory()

    first_bid = Bid(HandRank.ONE_PAIR, (10,))
    second_bid = Bid(HandRank.ONE_PAIR, (11,))

    history.add_bid("alice", first_bid, 1)
    history.add_bid("alice", second_bid, 2)

    # One repeated category should make the Detective
    # slightly more suspicious.
    assert detective.should_challenge(
        second_bid, 12, "alice", history
    ) is True


def test_non_detective_does_not_use_bid_patterns(monkeypatch):
    player = Player("bot", "Conservative")

    bot = Bot(player, BotPersonality.CONSERVATIVE)

    monkeypatch.setattr(
        "game.bot.probability_of_claim",
        lambda *args, **kwargs: 0.20
    )

    history = BidHistory()
    bid = Bid(HandRank.ONE_PAIR, (10,))

    history.add_bid("alice", bid, 1)

    assert bot.should_challenge(
        bid, 12, "alice", history
    ) is False
