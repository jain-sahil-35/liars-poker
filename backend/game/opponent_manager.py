from game.opponent_profile import OpponentProfile


class OpponentProfileManager:

    def __init__(self, player_ids):

        self.profiles = {
            player_id: OpponentProfile(player_id)
            for player_id in player_ids
        }

    def get_profile(self, player_id):

        if player_id not in self.profiles:
            raise KeyError(f"Unknown player: {player_id}")

        return self.profiles[player_id]

    def record_bid(self, player_id):

        self.get_profile(player_id).record_bid()

    def record_claim(self, player_id, is_true):

        self.get_profile(player_id).record_claim(is_true)

    def record_challenge(self, player_id, won):

        self.get_profile(player_id).record_challenge(won)

    def reset(self):

        for profile in self.profiles.values():
            profile.reset()