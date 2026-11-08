
class OpponentProfile:

    def __init__(self, player_id):
        self.player_id = player_id

        self.total_bids = 0
        self.bid_categories = {}

        self.challenges_won = 0
        self.challenges_lost = 0

        self.false_claims = 0
        self.true_claims = 0

    def record_bid(self, bid=None):
        self.total_bids += 1

        if bid is not None:
            category = bid.category
            self.bid_categories[category] = (
                self.bid_categories.get(category, 0) + 1
            )

    def category_frequency(self, category):
        if self.total_bids == 0:
            return 0.0

        return self.bid_categories.get(category, 0) / self.total_bids

    def record_claim(self, is_true):
        if is_true:
            self.true_claims += 1
        else:
            self.false_claims += 1

    def record_challenge(self, won):
        if won:
            self.challenges_won += 1
        else:
            self.challenges_lost += 1

    @property
    def false_claim_rate(self):
        total = self.false_claims + self.true_claims
        return (self.false_claims + 1) / (total + 2)

    @property
    def challenge_success_rate(self):
        total = self.challenges_won + self.challenges_lost

        if total == 0:
            return 0.0

        return self.challenges_won / total

    def reset(self):
        self.total_bids = 0
        self.bid_categories.clear()

        self.false_claims = 0
        self.true_claims = 0

        self.challenges_won = 0
        self.challenges_lost = 0
