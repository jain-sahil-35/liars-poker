from enum import Enum
import random

from game.bidding import Bid
from game.hand_evaluator import HandRank


class BotPersonality(str, Enum):
    CONSERVATIVE = "Conservative"
    AGGRESSIVE = "Aggressive"
    DETECTIVE = "Detective"


class Bot:

    def __init__(self, player, personality):
        self.player = player
        self.personality = personality

        # Track the number of challenges and bluffs.
        self.successful_challenges = 0
        self.failed_challenges = 0
        self.total_bids = 0

    @property
    def player_id(self):
        return self.player.player_id

    @property
    def name(self):
        return self.player.name

    def should_challenge(self, current_bid, total_cards):

        """
        Decide whether to challenge the current bid.

        This is an initial personality-based model.
        We'll replace it with probability calculations later.
        """

        if current_bid is None:
            return False

        # Initial challenge tendencies.
        thresholds = {
            BotPersonality.CONSERVATIVE: 0.30,
            BotPersonality.AGGRESSIVE: 0.10,
            BotPersonality.DETECTIVE: 0.25
        }

        probability = thresholds[self.personality]

        # The detective becomes more suspicious of
        # higher-ranking claims.
        if self.personality == BotPersonality.DETECTIVE:
            if current_bid.category >= HandRank.THREE_OF_A_KIND:
                probability += 0.20

        return random.random() < probability

    def choose_bid(self, current_bid):

        """
        Generate a higher bid than the current bid.

        Initial implementation supports pair,
        three of a kind and four of a kind claims.
        """

        candidates = []

        for category in [
            HandRank.ONE_PAIR,
            HandRank.THREE_OF_A_KIND,
            HandRank.FOUR_OF_A_KIND
        ]:

            for rank in range(2, 15):

                candidates.append(
                    Bid(category, (rank,))
                )

        candidates.sort(key=lambda bid: bid.strength)

        if current_bid is None:
            return Bid(HandRank.ONE_PAIR, (2,))

        higher_bids = [
            bid for bid in candidates
            if bid > current_bid
        ]

        if not higher_bids:
            return None

        if self.personality == BotPersonality.CONSERVATIVE:
            return higher_bids[0]

        if self.personality == BotPersonality.AGGRESSIVE:
            return random.choice(higher_bids)

        if self.personality == BotPersonality.DETECTIVE:
            return higher_bids[min(1, len(higher_bids) - 1)]

        return higher_bids[0]

    def decide_action(self, current_bid, total_cards):

        """
        Decide whether to challenge or raise.
        """

        if self.should_challenge(current_bid, total_cards):
            return "challenge", None

        bid = self.choose_bid(current_bid)

        if bid is None:
            return "challenge", None

        self.total_bids += 1

        return "bid", bid