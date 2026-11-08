
from enum import Enum
import random
from itertools import combinations

from game.cards import Rank, Suit
from game.bidding import Bid
from game.hand_evaluator import HandRank
from game.probability import probability_of_claim


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

    def generate_candidates(self):
        """Generate structurally valid bids for all ten categories."""

        candidates = []
        ranks = range(2, 15)

        # High Card
        for rank in ranks:
            candidates.append(
                Bid(HandRank.HIGH_CARD, (rank,))
            )

        # One Pair
        for rank in ranks:
            candidates.append(
                Bid(HandRank.ONE_PAIR, (rank,))
            )

        # Two Pair
        for high, low in combinations(ranks, 2):
            candidates.append(
                Bid(HandRank.TWO_PAIR, (low, high))
            )

        # Three of a Kind
        for rank in ranks:
            candidates.append(
                Bid(HandRank.THREE_OF_A_KIND, (rank,))
            )

        # Straight: 6-high through Ace-high.
        # Ace-low Straight is not permitted.
        for high in range(6, 15):
            candidates.append(
                Bid(HandRank.STRAIGHT, (high,))
            )

        # Flush: every suit and every possible high card.
        for suit in Suit:
            for rank in Rank:
                candidates.append(
                    Bid(HandRank.FLUSH, (suit, rank))
                )

        # Full House
        for trip in ranks:
            for pair in ranks:
                if trip != pair:
                    candidates.append(
                        Bid(HandRank.FULL_HOUSE, (trip, pair))
                    )

        # Four of a Kind
        for rank in ranks:
            candidates.append(
                Bid(HandRank.FOUR_OF_A_KIND, (rank,))
            )

        # Straight Flush: 6-high through King-high.
        # Ace-high is represented by Royal Flush.
        for high in range(6, 14):
            candidates.append(
                Bid(HandRank.STRAIGHT_FLUSH, (high,))
            )

        # Royal Flush
        candidates.append(
            Bid(HandRank.ROYAL_FLUSH, ())
        )

        return candidates

    def choose_bid(self, current_bid):
        """Choose a higher bid according to bot personality."""

        candidates = self.generate_candidates()
        candidates.sort(key=lambda bid: bid.strength)

        if current_bid is None:
            return Bid(HandRank.HIGH_CARD, (2,))

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

    def should_challenge(self, current_bid, total_cards, bidder_id=None):
        """Decide whether the current claim is likely to be false."""

        if current_bid is None:
            return False

        probability = probability_of_claim(
            self.player.cards,
            total_cards,
            current_bid
        )

        thresholds = {
            BotPersonality.CONSERVATIVE: 0.15,
            BotPersonality.AGGRESSIVE: 0.40,
            BotPersonality.DETECTIVE: 0.25,
        }

        threshold = thresholds[self.personality]

        # Detective adjusts suspicion using opponent history.
        if (
            self.personality == BotPersonality.DETECTIVE
            and self.opponent_manager is not None
            and bidder_id is not None
            and bidder_id != self.player_id
        ):
            profile = self.opponent_manager.get_profile(bidder_id)

            threshold += (
                profile.false_claim_rate - 0.5
            ) * 0.20

        return probability < threshold

    def decide_action(self, current_bid, total_cards, bidder_id=None):

        if self.should_challenge(current_bid, total_cards, bidder_id):
            return "challenge", None

        bid = self.choose_bid(current_bid)

        if bid is None:
            return "challenge", None

        self.total_bids += 1

        return "bid", bid
