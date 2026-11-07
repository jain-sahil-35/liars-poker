from game.cards import Rank, Suit


RANK_SYMBOLS = {
    Rank.TWO: "2",
    Rank.THREE: "3",
    Rank.FOUR: "4",
    Rank.FIVE: "5",
    Rank.SIX: "6",
    Rank.SEVEN: "7",
    Rank.EIGHT: "8",
    Rank.NINE: "9",
    Rank.TEN: "10",
    Rank.JACK: "J",
    Rank.QUEEN: "Q",
    Rank.KING: "K",
    Rank.ACE: "A"
}


SUIT_SYMBOLS = {
    Suit.HEARTS: "♥",
    Suit.DIAMONDS: "♦",
    Suit.CLUBS: "♣",
    Suit.SPADES: "♠"
}


def format_card(card):
    """Convert a Card object into a readable symbol."""

    rank = RANK_SYMBOLS[card.rank]
    suit = SUIT_SYMBOLS[card.suit]

    return f"{rank}{suit}"


def format_cards(cards):
    """Format a collection of cards."""

    return "  ".join(format_card(card) for card in cards)


def format_player(player, reveal=False):
    """Display player information without exposing hidden cards."""

    if player.eliminated:
        return f"{player.name} [ELIMINATED]"

    if reveal:
        return (
            f"{player.name} | "
            f"{format_cards(player.cards)}"
        )

    return (
        f"{player.name} | "
        f"{player.card_count} cards"
    )


def format_table(players, human_id):
    """Display the table while keeping opponents' cards hidden."""

    lines = []

    lines.append("=" * 40)
    lines.append("          LIAR'S POKER")
    lines.append("=" * 40)

    for player in players:

        reveal = player.player_id == human_id

        lines.append(
            format_player(player, reveal=reveal)
        )

    lines.append("=" * 40)

    return "\n".join(lines)