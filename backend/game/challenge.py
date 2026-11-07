from dataclasses import dataclass

from game.bidding import Bid
from game.claim_verifier import claim_exists


@dataclass(frozen=True)
class ChallengeResult:
    bid: Bid
    claim_is_true: bool
    bidder_id: str
    challenger_id: str
    loser_id: str


def resolve_challenge(
    cards_by_player,
    bidder_id,
    challenger_id,
    bid
):
    """
    Reveal all cards, verify the last bid,
    and determine who loses the challenge.
    """

    if bidder_id not in cards_by_player:
        raise ValueError("Bidder does not exist.")

    if challenger_id not in cards_by_player:
        raise ValueError("Challenger does not exist.")

    if bidder_id == challenger_id:
        raise ValueError("Bidder cannot challenge themselves.")

    if not isinstance(bid, Bid):
        raise TypeError("Expected a Bid object.")

    # Combine cards from every player.
    all_cards = []

    for player_cards in cards_by_player.values():
        all_cards.extend(player_cards)

    # Verify the claim.
    is_true = claim_exists(all_cards, bid)

    # Determine the loser.
    loser_id = (
        challenger_id if is_true else bidder_id
    )

    return ChallengeResult(
        bid=bid,
        claim_is_true=is_true,
        bidder_id=bidder_id,
        challenger_id=challenger_id,
        loser_id=loser_id
    )