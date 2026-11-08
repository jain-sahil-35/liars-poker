
from enum import Enum
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

        self.last_claim_probability = None
        self.last_challenge_threshold = None
        self.last_bid_probability = None

        # Desired probability that a bid is true.
        self.bid_confidence = {
            BotPersonality.CONSERVATIVE: 0.75,
            BotPersonality.AGGRESSIVE: 0.35,
            BotPersonality.DETECTIVE: 0.60,
        }

        # Limit expensive probability calculations.
        self.max_bid_candidates = 12
        self.bid_simulations = 500

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
            candidates.append(Bid(HandRank.HIGH_CARD, (rank,)))

        # One Pair
        for rank in ranks:
            candidates.append(Bid(HandRank.ONE_PAIR, (rank,)))

        # Two Pair
        for high, low in combinations(ranks, 2):
            candidates.append(Bid(HandRank.TWO_PAIR, (low, high)))

        # Three of a Kind
        for rank in ranks:
            candidates.append(Bid(HandRank.THREE_OF_A_KIND, (rank,)))

        # Straight: 6-high through Ace-high.
        for high in range(6, 15):
            candidates.append(Bid(HandRank.STRAIGHT, (high,)))

        # Flush
        for suit in Suit:
            for rank in Rank:
                candidates.append(Bid(HandRank.FLUSH, (suit, rank)))

        # Full House
        for trip in ranks:
            for pair in ranks:
                if trip != pair:
                    candidates.append(
                        Bid(HandRank.FULL_HOUSE, (trip, pair))
                    )

        # Four of a Kind
        for rank in ranks:
            candidates.append(Bid(HandRank.FOUR_OF_A_KIND, (rank,)))

        # Straight Flush: 6-high through King-high.
        for high in range(6, 14):
            candidates.append(Bid(HandRank.STRAIGHT_FLUSH, (high,)))

        # Royal Flush: generate one candidate for each suit.
        for suit in Suit:
            candidates.append(
                Bid(HandRank.ROYAL_FLUSH, (suit,))
            )

        return candidates

    def _card_support(self, bid):
        """
        Estimate how much the bot's own cards support a claim.

        This is a ranking heuristic, not the probability that
        the claim exists among all players' cards.
        """

        cards = self.player.cards

        if not cards:
            return 0.0

        rank_counts = {}

        for card in cards:
            rank_counts[card.rank.value] = (
                rank_counts.get(card.rank.value, 0) + 1
            )

        category = bid.category
        values = bid.values

        if category == HandRank.HIGH_CARD:
            return min(rank_counts.get(values[0], 0), 1)

        if category == HandRank.ONE_PAIR:
            return min(rank_counts.get(values[0], 0), 2) / 2

        if category == HandRank.TWO_PAIR:
            matches = (
                min(rank_counts.get(values[0], 0), 2)
                + min(rank_counts.get(values[1], 0), 2)
            )
            return matches / 4

        if category == HandRank.THREE_OF_A_KIND:
            return min(rank_counts.get(values[0], 0), 3) / 3

        if category == HandRank.FOUR_OF_A_KIND:
            return min(rank_counts.get(values[0], 0), 4) / 4

        if category == HandRank.STRAIGHT:
            high = values[0]
            required = set(range(high - 4, high + 1))
            matches = len(required.intersection(rank_counts.keys()))
            return matches / 5

        if category == HandRank.FLUSH:
            suit, high_card = values
            matches = sum(
                1 for card in cards
                if card.suit == suit and card.rank <= high_card
            )
            return min(matches, 5) / 5

        if category == HandRank.FULL_HOUSE:
            trip, pair = values
            matches = (
                min(rank_counts.get(trip, 0), 3)
                + min(rank_counts.get(pair, 0), 2)
            )
            return matches / 5

        if category == HandRank.STRAIGHT_FLUSH:
            high = values[0]
            required = set(range(high - 4, high + 1))

            best_matches = 0

            for suit in Suit:
                matches = {
                    card.rank.value
                    for card in cards
                    if card.suit == suit
                    and card.rank.value in required
                }
                best_matches = max(best_matches, len(matches))

            return best_matches / 5

        if category == HandRank.ROYAL_FLUSH:
            required = {10, 11, 12, 13, 14}

            best_matches = 0

            for suit in Suit:
                matches = {
                    card.rank.value
                    for card in cards
                    if card.suit == suit
                    and card.rank.value in required
                }
                best_matches = max(best_matches, len(matches))

            return best_matches / 5

        return 0.0

    def _get_candidate_pool(self, current_bid):
        """Return a small set of promising legal bids."""

        candidates = self.generate_candidates()

        if current_bid is not None:
            candidates = [
                bid for bid in candidates
                if bid > current_bid
            ]

        candidates.sort(
            key=lambda bid: (
                -self._card_support(bid),
                bid.strength
            )
        )

        return candidates[:self.max_bid_candidates]

    def choose_bid(self, current_bid, total_cards=None):
        """Choose a bid using hand support and probability."""

        if total_cards is None:
            total_cards = max(len(self.player.cards), 6)

        candidates = self._get_candidate_pool(current_bid)

        if not candidates:
            self.last_bid_probability = None
            return None

        evaluated = []

        for bid in candidates:
            probability = probability_of_claim(
                self.player.cards,
                total_cards,
                bid,
                simulations=self.bid_simulations
            )

            evaluated.append((bid, probability))

        target = self.bid_confidence[self.personality]

        # Prefer the strongest bid that meets the confidence target.
        acceptable = [
            (bid, probability)
            for bid, probability in evaluated
            if probability >= target
        ]

        if acceptable:
            chosen_bid, probability = max(
                acceptable,
                key=lambda item: item[0].strength
            )
        else:
            # If none meet the target, choose the most probable claim.
            chosen_bid, probability = max(
                evaluated,
                key=lambda item: (
                    item[1],
                    item[0].strength
                )
            )

        self.last_bid_probability = probability

        return chosen_bid

    def _get_pattern_suspicion(self, current_bid, bidder_id, bid_history):
        """
        Estimate extra suspicion from an opponent's bidding patterns.
        Returns a small threshold adjustment.
        """

        if bidder_id is None or bidder_id == self.player_id:
            return 0.0

        if bid_history is None:
            return 0.0

        # Check the opponent's bids in the current round.
        player_bids = bid_history.get_player_bids(bidder_id)

        repeated_count = sum(
            record.bid.category == current_bid.category
            for record in player_bids
        )

        # Repeated use of the same category this round.
        round_bonus = min(max(repeated_count - 1, 0) * 0.05, 0.10)

        # Check the opponent's long-term category preference.
        profile = self.opponent_manager.get_profile(bidder_id)

        category_bonus = 0.0

        if profile.total_bids >= 4:
            frequency = profile.category_frequency(current_bid.category)

            if frequency >= 0.50:
                category_bonus = 0.03

        return round_bonus + category_bonus

    def should_challenge(
        self,
        current_bid,
        total_cards,
        bidder_id=None,
        bid_history=None
    ):
        """Decide whether the current claim is likely to be false."""

        if current_bid is None:
            return False

        probability = probability_of_claim(
            self.player.cards,
            total_cards,
            current_bid
        )

        self.last_claim_probability = probability

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

            threshold += self._get_pattern_suspicion(
                current_bid,
                bidder_id,
                bid_history
            )

        self.last_challenge_threshold = threshold

        return probability < threshold

    def decide_action(
        self,
        current_bid,
        total_cards,
        bidder_id=None,
        bid_history=None
    ):

        if self.should_challenge(
            current_bid,
            total_cards,
            bidder_id,
            bid_history
        ):
            return "challenge", None

        bid = self.choose_bid(current_bid, total_cards)

        if bid is None:
            return "challenge", None

        self.total_bids += 1

        return "bid", bid
