from dataclasses import dataclass

from game.bidding import Bid


@dataclass
class BidRecord:
    player_id: str
    bid: Bid
    turn_number: int


class BidHistory:

    def __init__(self):
        self.records = []

    def add_bid(self, player_id, bid, turn_number):

        if not isinstance(bid, Bid):
            raise TypeError("Expected a Bid object.")

        if turn_number < 1:
            raise ValueError("Turn number must be positive.")

        record = BidRecord(
            player_id=player_id,
            bid=bid,
            turn_number=turn_number
        )

        self.records.append(record)

    def get_history(self):
        return self.records.copy()

    def get_player_bids(self, player_id):

        return [
            record
            for record in self.records
            if record.player_id == player_id
        ]

    def latest_bid(self):

        if not self.records:
            return None

        return self.records[-1]

    def reset(self):
        self.records.clear()

    def __len__(self):
        return len(self.records)