from enum import Enum
import random

from game.bidding import Bid
from game.hand_evaluator import HandRank

from game.probability import probability_of_rank_claim
from game.cards import Rank


class BotPersonality(str, Enum):
    CONSERVATIVE = "Conservative"
    AGGRESSIVE = "Aggressive"
    DETECTIVE = "Detective"


class Bot:

    def __init__(self, player, personality, opponent_manager=None):
        self.player = player
        self.personality = personality
        self.opponent_manager = opponent_manager

        self.successful_challenges = 0
        self.failed_challenges = 0
        self.total_bids = 0

    @property
    def player_id(self):
        return self.player.player_id

    @property
    def name(self):
        return self.player.name

    def should_challenge(self, current_bid, total_cards, bidder_id=None):

        if current_bid is None:
            return False

        required_counts = {
            HandRank.ONE_PAIR: 2,
            HandRank.THREE_OF_A_KIND: 3,
            HandRank.FOUR_OF_A_KIND: 4
        }

        if current_bid.category not in required_counts:
            return False

        claimed_rank = Rank(current_bid.values[0])
        required_count = required_counts[current_bid.category]

        probability = probability_of_rank_claim(
            self.player.cards,
            total_cards,
            claimed_rank,
            required_count
        )

        thresholds = {
            BotPersonality.CONSERVATIVE: 0.15,
            BotPersonality.AGGRESSIVE: 0.40,
            BotPersonality.DETECTIVE: 0.25
        }

        threshold = thresholds[self.personality]

        # Adjust the Detective's suspicion using opponent history.
        if (
            self.personality == BotPersonality.DETECTIVE
            and self.opponent_manager is not None
            and bidder_id is not None
            and bidder_id != self.player_id
        ):
            profile = self.opponent_manager.get_profile(bidder_id)

            threshold += (profile.false_claim_rate - 0.5) * 0.20

        return probability < threshold

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

    def decide_action(self, current_bid, total_cards, bidder_id=None):

        if self.should_challenge(current_bid, total_cards, bidder_id):
            return "challenge", None

        bid = self.choose_bid(current_bid)

        if bid is None:
            return "challenge", None

        self.total_bids += 1
        return "bid", bid