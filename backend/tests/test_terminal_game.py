from game.terminal_game import get_human_bid
from game.hand_evaluator import HandRank

def test_human_can_make_high_card_bid():

    inputs = iter(["1", "A"])

    bid = get_human_bid(
        current_bid=None,
        input_fn=lambda prompt: next(inputs)
    )

    assert bid.category == HandRank.HIGH_CARD
    assert bid.values == (14,)