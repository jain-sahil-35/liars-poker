from math import comb
from game.cards import Card, Rank

def probability_of_at_least(
    required: int,
    available_successes: int,
    unknown_cards: int,
    unknown_total: int
) -> float:

    if required <= 0:
        return 1.0

    if required > available_successes:
        return 0.0

    probability = 0.0

    for successes in range(required, min(available_successes, unknown_cards) + 1):

        failures = unknown_cards - successes

        if failures > unknown_total - available_successes:
            continue

        ways = (
            comb(available_successes, successes)
            * comb(unknown_total - available_successes, failures)
        )

        total_ways = comb(unknown_total, unknown_cards)

        probability += ways / total_ways

    return probability

def probability_of_rank_claim(
    player_cards: list[Card],
    total_cards: int,
    rank: Rank,
    required_count: int
) -> float:

    if not 0 <= total_cards <= 52:
        raise ValueError("Total cards must be between 0 and 52.")

    if len(player_cards) > total_cards:
        raise ValueError("Player cannot hold more cards than are in play.")

    if not 1 <= required_count <= 4:
        raise ValueError("Required count must be between 1 and 4.")

    if any(not isinstance(card, Card) for card in player_cards):
        raise TypeError("All player cards must be Card objects.")

    known_count = sum(
        1 for card in player_cards
        if card.rank == rank
    )

    remaining_required = required_count - known_count

    available_successes = 4 - known_count

    unknown_cards = total_cards - len(player_cards)

    unknown_total = 52 - len(player_cards)

    return probability_of_at_least(
        remaining_required,
        available_successes,
        unknown_cards,
        unknown_total
    )