from game.deck import Deck
from game.player import Player
from game.bidding import BidManager
from game.challenge import resolve_challenge
from game.bid_history import BidHistory
from game.opponent_manager import OpponentProfileManager


class GameState:

    def __init__(self, players, bots=None):

        if not 2 <= len(players) <= 8:
            raise ValueError("A game requires 2 to 8 players.")

        player_ids = [player.player_id for player in players]

        if len(set(player_ids)) != len(player_ids):
            raise ValueError("Player IDs must be unique.")

        self.players = players

        self.deck = Deck()
        self.bid_manager = BidManager()
        self._bidder_id = None

        # Track bids made during the current round.
        self.bid_history = BidHistory()

        # Track opponent behaviour throughout the game.
        self.opponent_manager = OpponentProfileManager(player_ids)

        # Register bots and connect them to the shared opponent manager.
        self.bots = {}

        for player_id, bot in (bots or {}).items():

            player = self.get_player(player_id)

            if bot.player_id != player_id:
                raise ValueError("Bot ID does not match its registered player ID.")

            if bot.player is not player:
                raise ValueError("Bot must reference the same Player object used by GameState.")

            bot.opponent_manager = self.opponent_manager
            self.bots[player_id] = bot

        self.current_turn_index = 0

        self.last_loser_id = None

        self.round_number = 0

        self.started = False
        self.round_resolved = False
        self.finished = False

    @property
    def active_players(self):
        """Return players who have not been eliminated."""

        return [
            player
            for player in self.players
            if not player.eliminated
        ]

    @property
    def winner(self):
        """Return the winner if only one player remains."""

        if len(self.active_players) == 1:
            return self.active_players[0]

        return None

    @property
    def current_player(self):
        """Return the player whose turn it currently is."""

        if not self.started or self.finished or self.round_resolved:
            return None

        active = self.active_players

        if not active or not (0 <= self.current_turn_index < len(active)):
            return None

        return active[self.current_turn_index]

    def get_player(self, player_id):

        for player in self.players:

            if player.player_id == player_id:
                return player

        raise ValueError("Player not found.")

    def start_game(self):
        """Start the match and deal the first round."""

        if self.started:
            raise ValueError("Game has already started.")

        self.started = True

        self.start_round()

    def start_round(self):
        """Prepare and deal a new round."""

        if self.finished:
            raise ValueError("Game has already finished.")

        active = self.active_players

        if len(active) <= 1:
            self.finished = True
            return

        # Create a fresh shuffled deck.
        self.deck.reset()

        # Reset bidding.
        self.bid_manager.reset()
        self._bidder_id = None

        # Reset current-round bid history.
        self.bid_history.reset()

        self.round_resolved = False

        # Collect cards from the previous round.
        for player in active:
            player.clear_cards()

        # Deal cards according to each player's hand size.
        for player in active:
            cards = self.deck.deal(player.hand_size)
            player.receive_cards(cards)

        self.round_number += 1

        # Determine who starts.
        if self.last_loser_id is None:
            self.current_turn_index = 0

        else:
            loser_index = next(
                i for i, player in enumerate(active)
                if player.player_id == self.last_loser_id
            ) if any(
                player.player_id == self.last_loser_id
                for player in active
            ) else None

            if loser_index is None:
                original_index = next(
                    i for i, player in enumerate(self.players)
                    if player.player_id == self.last_loser_id
                )

                for offset in range(1, len(self.players) + 1):
                    candidate = self.players[
                        (original_index + offset) % len(self.players)
                    ]

                    if not candidate.eliminated:
                        self.current_turn_index = active.index(candidate)
                        break

            else:
                self.current_turn_index = (
                    loser_index + 1
                ) % len(active)

    def next_turn(self):
        """Move clockwise to the next active player."""

        if not self.started or self.finished:
            raise ValueError("No active game.")

        active = self.active_players

        self.current_turn_index = (
            self.current_turn_index + 1
        ) % len(active)

        return self.current_player

    def place_bid(self, player_id, bid):
        """Allow the current player to make a bid."""

        if not self.started or self.finished:
            raise ValueError("No active game.")

        if self.current_player.player_id != player_id:
            raise ValueError("It is not this player's turn.")

        self.bid_manager.place_bid(bid)
        self._bidder_id = player_id

        # Record the bid in the current round's history.
        turn_number = len(self.bid_history) + 1

        self.bid_history.add_bid(
            player_id,
            bid,
            turn_number
        )

        # Update the player's long-term statistics.
        self.opponent_manager.record_bid(player_id, bid)

        return bid

    def call_bullshit(self, challenger_id):
        """Resolve a challenge and apply the penalty."""

        if not self.started or self.finished:
            raise ValueError("No active game.")

        if self.current_player.player_id != challenger_id:
            raise ValueError("It is not this player's turn.")

        if self.bidder_id == challenger_id:
            raise ValueError("A player cannot challenge their own bid.")

        bid = self.bid_manager.call_bullshit()

        bidder_id = self.bidder_id

        cards_by_player = {
            player.player_id: player.cards.copy()
            for player in self.active_players
        }

        result = resolve_challenge(
            cards_by_player,
            bidder_id,
            challenger_id,
            bid
        )

        # Apply the penalty to the loser.
        loser = self.get_player(result.loser_id)

        loser.add_penalty_card()

        # Record whether the bidder's claim was true or false.
        self.opponent_manager.record_claim(
            bidder_id,
            result.claim_is_true
        )

        # Record the challenger's performance.
        challenge_won = not result.claim_is_true

        self.opponent_manager.record_challenge(
            challenger_id,
            challenge_won
        )

        self.last_loser_id = loser.player_id
        self.round_resolved = True

        # End the match if only one player remains.
        if len(self.active_players) <= 1:
            self.finished = True

        return result

    @property
    def bidder_id(self):
        """ID of the player who made the current bid."""

        return self._bidder_id
    
    def start_next_round(self):
        """Start another round after the previous challenge."""

        if not self.round_resolved:
            raise ValueError(
                "Cannot start a new round before resolving the current one."
            )

        if self.finished:
            raise ValueError("The game has already finished.")

        self.start_round()

    def process_bot_turn(self):
        """
        Process one complete turn for the current bot.

        A bot either places a bid or challenges the previous bid.
        """

        if not self.started or self.finished:
            raise ValueError("No active game.")

        if self.round_resolved:
            raise ValueError("The current round has already been resolved.")

        player = self.current_player

        if player.player_id not in self.bots:
            raise ValueError("The current player is not a bot.")

        bot = self.bots[player.player_id]

        total_cards = sum(
            active_player.card_count
            for active_player in self.active_players
        )

        action, bid = bot.decide_action(
            self.bid_manager.current_bid,
            total_cards,
            self.bidder_id,
            self.bid_history
        )

        if action == "challenge":

            result = self.call_bullshit(player.player_id)

            if result.claim_is_true:
                bot.failed_challenges += 1
            else:
                bot.successful_challenges += 1

            return "challenge", result

        if action == "bid":

            if bid is None:
                raise ValueError("Bot selected bid action without providing a bid.")

            self.place_bid(player.player_id, bid)

            self.next_turn()

            return "bid", bid

        raise ValueError(f"Unknown bot action: {action}")