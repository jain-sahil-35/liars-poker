from game.bot import Bot, BotPersonality
from game.player import Player
from game.bidding import Bid
from game.hand_evaluator import HandRank
from game.cards import Card, Rank, Suit

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


def test_bot_makes_first_bid():

    bot = create_bot(BotPersonality.CONSERVATIVE)

    bid = bot.choose_bid(None)

    assert bid.category == HandRank.ONE_PAIR
    assert bid.values == (2,)


def test_bot_raises_current_bid():

    bot = create_bot(BotPersonality.CONSERVATIVE)

    current_bid = Bid(HandRank.ONE_PAIR, (10,))

    new_bid = bot.choose_bid(current_bid)

    assert new_bid > current_bid


def test_conservative_bot_chooses_smallest_raise():

    bot = create_bot(BotPersonality.CONSERVATIVE)

    current_bid = Bid(HandRank.ONE_PAIR, (10,))

    new_bid = bot.choose_bid(current_bid)

    assert new_bid == Bid(HandRank.ONE_PAIR, (11,))


def test_aggressive_bot_chooses_higher_bid():

    bot = create_bot(BotPersonality.AGGRESSIVE)

    current_bid = Bid(HandRank.ONE_PAIR, (10,))

    new_bid = bot.choose_bid(current_bid)

    assert new_bid > current_bid


def test_bot_decision_format():

    bot = create_bot(BotPersonality.CONSERVATIVE)

    action, bid = bot.decide_action(None, 6)

    assert action == "bid"
    assert bid is not None


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