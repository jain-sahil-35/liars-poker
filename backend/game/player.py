from dataclasses import dataclass, field

from game.cards import Card


@dataclass
class Player:

    player_id: str
    name: str

    cards: list[Card] = field(default_factory=list)

    hand_size: int = 2

    eliminated: bool = False

    @property
    def card_count(self):
        """Number of cards currently held."""
        return len(self.cards)

    def receive_cards(self, new_cards):
        """Add newly dealt cards to the player's hand."""

        if self.eliminated:
            raise ValueError("Eliminated players cannot receive cards.")

        self.cards.extend(new_cards)

    def clear_cards(self):
        """Collect cards at the end of a round."""

        self.cards.clear()

    def add_penalty_card(self):
        """Increase the number of cards for the next round."""

        if self.eliminated:
            raise ValueError("Player is already eliminated.")

        self.hand_size += 1

        if self.hand_size >= 6:
            self.eliminate()

    def eliminate(self):
        """Eliminate the player from the match."""

        self.eliminated = True
        self.clear_cards()