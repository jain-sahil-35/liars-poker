from math import comb
import random

from game.cards import Card, Rank, Suit
from game.bidding import Bid
from game.hand_evaluator import HandRank
from collections import Counter


def probability_of_at_least(
    required: int,
    available_successes: int,
    unknown_cards: int,
    unknown_total: int
) -> float:
    """Calculate a hypergeometric probability."""

    if required <= 0:
        return 1.0

    if (
        available_successes < 0
        or unknown_cards < 0
        or unknown_total < 0
        or available_successes > unknown_total
        or unknown_cards > unknown_total
    ):
        raise ValueError("Invalid hypergeometric parameters.")

    if required > available_successes or required > unknown_cards:
        return 0.0

    total_ways = comb(unknown_total, unknown_cards)

    probability = 0.0

    for successes in range(
        required,
        min(available_successes, unknown_cards) + 1
    ):
        failures = unknown_cards - successes

        if failures > unknown_total - available_successes:
            continue

        ways = (
            comb(available_successes, successes)
            * comb(unknown_total - available_successes, failures)
        )

        probability += ways / total_ways

    return probability


def probability_of_rank_claim(
    player_cards: list[Card],
    total_cards: int,
    rank: Rank,
    required_count: int
) -> float:
    """Estimate the probability of finding a required number of one rank."""

    if not 0 <= total_cards <= 52:
        raise ValueError("Total cards must be between 0 and 52.")

    if len(player_cards) > total_cards:
        raise ValueError("Player cannot hold more cards than are in play.")

    if not 1 <= required_count <= 4:
        raise ValueError("Required count must be between 1 and 4.")

    if any(not isinstance(card, Card) for card in player_cards):
        raise TypeError("All player cards must be Card objects.")

    if not isinstance(rank, Rank):
        raise TypeError("Rank must be a Rank object.")

    if len(set(player_cards)) != len(player_cards):
        raise ValueError("Player cards cannot contain duplicates.")

    known_count = sum(
        1 for card in player_cards
        if card.rank == rank
    )

    remaining_required = required_count - known_count

    if remaining_required <= 0:
        return 1.0

    available_successes = 4 - known_count
    unknown_cards = total_cards - len(player_cards)
    unknown_total = 52 - len(player_cards)

    return probability_of_at_least(
        remaining_required,
        available_successes,
        unknown_cards,
        unknown_total
    )


def _claim_exists_fast(cards, bid):
    """
    Check a claim using rank and suit counts instead
    of generating every possible card combination.
    """

    rank_counts = Counter(card.rank.value for card in cards)

    def has_straight(high_rank, suit=None):
        if high_rank == 5:
            required = {14, 2, 3, 4, 5}
        else:
            required = set(range(high_rank - 4, high_rank + 1))

        available = {
            card.rank.value
            for card in cards
            if suit is None or card.suit == suit
        }

        return required.issubset(available)

    category = bid.category
    values = bid.values

    if category == HandRank.HIGH_CARD:
        return rank_counts[values[0]] >= 1

    if category == HandRank.ONE_PAIR:
        return rank_counts[values[0]] >= 2

    if category == HandRank.TWO_PAIR:
        high, low = values
        return rank_counts[high] >= 2 and rank_counts[low] >= 2

    if category == HandRank.THREE_OF_A_KIND:
        return rank_counts[values[0]] >= 3

    if category == HandRank.FOUR_OF_A_KIND:
        return rank_counts[values[0]] >= 4

    if category == HandRank.STRAIGHT:
        high = values[0]

        if not has_straight(high):
            return False

        required = (
            {14, 2, 3, 4, 5}
            if high == 5
            else set(range(high - 4, high + 1))
        )

        suit_options = [
            {
                card.suit
                for card in cards
                if card.rank.value == rank
            }
            for rank in required
        ]

        # If all available cards for these ranks have only
        # one common suit, the only possible straight is a
        # Straight Flush.
        return len(set.union(*suit_options)) > 1

    if category == HandRank.FULL_HOUSE:
        trip, pair = values
        return rank_counts[trip] >= 3 and rank_counts[pair] >= 2

    if category == HandRank.FLUSH:
        # A Flush must contain five distinct ranks.
        if len(set(values)) != 5:
            return False

        # A consecutive sequence is classified as a Straight Flush,
        # not an ordinary Flush.
        sorted_ranks = sorted(values)

        is_straight = (
            sorted_ranks == [2, 3, 4, 5, 14]
            or sorted_ranks[-1] - sorted_ranks[0] == 4
        )

        if is_straight:
            return False

        for suit in Suit:
            suit_counts = Counter(
                card.rank.value
                for card in cards
                if card.suit == suit
            )

            if all(suit_counts[rank] >= 1 for rank in values):
                return True

        return False

    if category == HandRank.STRAIGHT_FLUSH:
        # Ace-high Straight Flush is classified as Royal Flush.
        if values[0] == 14:
            return False

        return any(
            has_straight(values[0], suit)
            for suit in Suit
        )

    if category == HandRank.ROYAL_FLUSH:
        required = {10, 11, 12, 13, 14}

        for suit in Suit:
            available = {
                card.rank.value
                for card in cards
                if card.suit == suit
            }

            if required.issubset(available):
                return True

        return False

    return False

def probability_of_claim(
    player_cards: list[Card],
    total_cards: int,
    bid: Bid,
    simulations: int = 5000,
    rng=None
) -> float:
    """
    Estimate the probability that a bid exists among all cards in play.

    Uses exact hypergeometric calculations for rank-based claims
    and Monte Carlo simulation for other categories.
    """

    if not isinstance(bid, Bid):
        raise TypeError("Expected a Bid object.")

    if not 0 <= total_cards <= 52:
        raise ValueError("Total cards must be between 0 and 52.")

    if len(player_cards) > total_cards:
        raise ValueError("Player cannot hold more cards than are in play.")

    if any(not isinstance(card, Card) for card in player_cards):
        raise TypeError("All player cards must be Card objects.")

    if len(set(player_cards)) != len(player_cards):
        raise ValueError("Player cards cannot contain duplicates.")

    if not isinstance(simulations, int) or isinstance(simulations, bool):
        raise TypeError("Simulations must be an integer.")

    if simulations <= 0:
        raise ValueError("Simulations must be positive.")

    if len(player_cards) > total_cards:
        raise ValueError("Invalid number of cards.")

    if total_cards < {
        HandRank.HIGH_CARD: 1,
        HandRank.ONE_PAIR: 2,
        HandRank.TWO_PAIR: 4,
        HandRank.THREE_OF_A_KIND: 3,
        HandRank.STRAIGHT: 5,
        HandRank.FLUSH: 5,
        HandRank.FULL_HOUSE: 5,
        HandRank.FOUR_OF_A_KIND: 4,
        HandRank.STRAIGHT_FLUSH: 5,
        HandRank.ROYAL_FLUSH: 5
    }[bid.category]:
        return 0.0

    # These categories can be calculated exactly.
    rank_claims = {
        HandRank.HIGH_CARD: 1,
        HandRank.ONE_PAIR: 2,
        HandRank.THREE_OF_A_KIND: 3,
        HandRank.FOUR_OF_A_KIND: 4
    }

    if bid.category in rank_claims:
        return probability_of_rank_claim(
            player_cards,
            total_cards,
            Rank(bid.values[0]),
            rank_claims[bid.category]
        )

    # Build the unseen portion of the standard deck.
    full_deck = [
        Card(rank, suit)
        for rank in Rank
        for suit in Suit
    ]

    known_cards = set(player_cards)

    unknown_deck = [
        card for card in full_deck
        if card not in known_cards
    ]

    unknown_count = total_cards - len(player_cards)

    if rng is None:
        rng = random

    successful_simulations = 0

    for _ in range(simulations):

        sampled_cards = rng.sample(
            unknown_deck,
            unknown_count
        )

        all_cards = player_cards + sampled_cards

        if _claim_exists_fast(all_cards, bid):
            successful_simulations += 1

    return successful_simulations / simulations
