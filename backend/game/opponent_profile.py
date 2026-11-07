class OpponentProfile:

    def __init__(self, player_id):

        self.player_id = player_id

        self.total_bids = 0

        self.challenges_won = 0
        self.challenges_lost = 0

        self.false_claims = 0
        self.true_claims = 0

    def record_bid(self):
        self.total_bids += 1

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

        self.false_claims = 0
        self.true_claims = 0

        self.challenges_won = 0
        self.challenges_lost = 0