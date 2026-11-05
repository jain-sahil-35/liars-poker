from game.cards import Card, Rank, Suit


def test_card_creation():
    card = Card(Rank.ACE, Suit.HEARTS)

    assert card.rank == Rank.ACE
    assert card.suit == Suit.HEARTS


def test_card_string():
    card = Card(Rank.KING, Suit.SPADES)

    assert str(card) == "KING of Spades"


def test_rank_comparison():
    assert Rank.ACE > Rank.KING
    assert Rank.KING > Rank.QUEEN
    assert Rank.TWO < Rank.THREE


def test_cards_are_immutable():
    card = Card(Rank.ACE, Suit.HEARTS)

    try:
        card.rank = Rank.KING
        assert False, "Card should be immutable"
    except AttributeError:
        pass