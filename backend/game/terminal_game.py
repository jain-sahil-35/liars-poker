
from game.player import Player
from game.game_state import GameState
from game.bot import Bot, BotPersonality
from game.bidding import Bid
from game.hand_evaluator import HandRank
from game.terminal_ui import format_table
from game.cards import Rank, Suit


RANKS = {
    "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9,
    "10": 10, "J": 11, "Q": 12,
    "K": 13, "A": 14
}

BID_CATEGORIES = {
    "1": HandRank.HIGH_CARD,
    "2": HandRank.ONE_PAIR,
    "3": HandRank.TWO_PAIR,
    "4": HandRank.THREE_OF_A_KIND,
    "5": HandRank.STRAIGHT,
    "6": HandRank.FLUSH,
    "7": HandRank.FULL_HOUSE,
    "8": HandRank.FOUR_OF_A_KIND,
    "9": HandRank.STRAIGHT_FLUSH,
    "10": HandRank.ROYAL_FLUSH
}


def choose_option(prompt, valid_options, input_fn=input):
    """Ask until the user enters one of the allowed options."""

    while True:
        choice = input_fn(prompt).strip()

        if choice in valid_options:
            return choice

        print("Invalid choice. Try again.")


def create_players(input_fn=input):
    """Create one human player and the selected bot opponents."""

    print("\n=== PLAYER SETUP ===")

    bot_count = int(
        choose_option(
            "Number of bots (1-7): ",
            [str(i) for i in range(1, 8)],
            input_fn
        )
    )

    players = [Player("human", "You")]
    bots = {}

    personalities = list(BotPersonality)

    for i in range(1, bot_count + 1):

        print(f"\nChoose personality for Bot {i}:")

        for index, personality in enumerate(personalities, 1):
            print(f"{index}. {personality.value}")

        choice = choose_option(
            "Your choice: ",
            ["1", "2", "3"],
            input_fn
        )

        player = Player(f"bot_{i}", f"Bot {i}")
        personality = personalities[int(choice) - 1]

        players.append(player)
        bots[player.player_id] = Bot(player, personality)

    return players, bots



def display_bid(bid):
    """Return a readable description of a bid."""

    if bid is None:
        return "No bids yet"

    rank_names = {
        11: "Jack",
        12: "Queen",
        13: "King",
        14: "Ace"
    }

    category = bid.category.name.replace("_", " ").title()

    if bid.category == HandRank.FLUSH:
        suit, high_card = bid.values
        rank_name = rank_names.get(high_card.value, str(high_card.value))
        return f"Flush - {suit.value} - {rank_name}"

    if bid.category == HandRank.STRAIGHT_FLUSH:
        suit, high_rank = bid.values
        rank_name = rank_names.get(high_rank, str(high_rank))
        return f"Straight Flush - {suit.value} - {rank_name}-high"

    if bid.category == HandRank.ROYAL_FLUSH:
        return f"Royal Flush - {bid.values[0].value}"

    values = ", ".join(
        rank_names.get(value, str(value))
        for value in bid.values
    )

    return f"{category} - {values}"


def get_human_bid(current_bid, input_fn=input):
    """Read and validate a human player's bid."""

    category_names = {
        "1": "High Card",
        "2": "One Pair",
        "3": "Two Pair",
        "4": "Three of a Kind",
        "5": "Straight",
        "6": "Flush",
        "7": "Full House",
        "8": "Four of a Kind",
        "9": "Straight Flush",
        "10": "Royal Flush"
    }

    value_counts = {
        HandRank.HIGH_CARD: 1,
        HandRank.ONE_PAIR: 1,
        HandRank.TWO_PAIR: 2,
        HandRank.THREE_OF_A_KIND: 1,
        HandRank.STRAIGHT: 1,
        HandRank.FLUSH: 2,
        HandRank.FULL_HOUSE: 2,
        HandRank.FOUR_OF_A_KIND: 1,
        HandRank.STRAIGHT_FLUSH: 2,
        HandRank.ROYAL_FLUSH: 1
    }

    def read_rank(prompt):
        while True:
            rank = input_fn(prompt).strip().upper()

            if rank in RANKS:
                return RANKS[rank]

            print("Invalid rank. Choose from 2-10, J, Q, K, A.")

    def read_suit():
        suits = {
            "1": Suit.HEARTS,
            "2": Suit.DIAMONDS,
            "3": Suit.CLUBS,
            "4": Suit.SPADES
        }

        print("\nChoose suit:")
        print("1. Hearts")
        print("2. Diamonds")
        print("3. Clubs")
        print("4. Spades")

        choice = choose_option(
            "Your choice: ",
            ["1", "2", "3", "4"],
            input_fn
        )

        return suits[choice]

    while True:

        print("\nAvailable claims:")

        for key, name in category_names.items():
            print(f"{key}. {name}")

        category_choice = choose_option(
            "Choose category: ",
            list(category_names.keys()),
            input_fn
        )

        category = BID_CATEGORIES[category_choice]

        if category == HandRank.FLUSH:
            suit = read_suit()
            high_card = Rank(read_rank(
                "Enter the Flush high card (2-10, J, Q, K, A): "
            ))

            values = (suit, high_card)

        elif category == HandRank.STRAIGHT_FLUSH:
            suit = read_suit()
            high_rank = read_rank(
                "Enter the Straight Flush high card (6-10, J, Q, K): "
            )
            values = (suit, high_rank)

        elif category == HandRank.ROYAL_FLUSH:
            suit = read_suit()
            values = (suit,)

        else:
            count = value_counts[category]
            values = []

            if category == HandRank.TWO_PAIR:
                print("Enter the higher pair rank first.")

            elif category == HandRank.FULL_HOUSE:
                print(
                    "Enter the three-of-a-kind rank first, "
                    "then the pair rank."
                )

            for i in range(count):

                if category == HandRank.TWO_PAIR:
                    prompt = f"Pair {i + 1} rank: "

                elif category == HandRank.FULL_HOUSE:
                    prompt = (
                        "Three-of-a-kind rank: "
                        if i == 0 else "Pair rank: "
                    )

                else:
                    prompt = "Choose rank (2-10, J, Q, K, A): "

                values.append(read_rank(prompt))

            values = tuple(values)

        try:
            bid = Bid(category, values)

        except (ValueError, TypeError) as error:
            print(f"Invalid bid: {error}")
            continue

        if current_bid is not None and not current_bid < bid:
            print("Your bid must be higher than the current bid.")
            continue

        return bid


def play_human_turn(game, input_fn=input):

    print("\nYour turn!")

    if game.bid_manager.current_bid is None:
        print("No current claim. You must make the first bid.")

    else:
        print(
            "Current claim:",
            display_bid(game.bid_manager.current_bid)
        )

        print("Last bidder:", game.bidder_id)

    if game.bid_manager.current_bid is None:
        action = "1"

    else:
        action = choose_option(
            "\n1. Make a higher bid\n2. Call Bullshit\nChoice: ",
            ["1", "2"],
            input_fn
        )

    if action == "1":

        bid = get_human_bid(
            game.bid_manager.current_bid,
            input_fn
        )

        game.place_bid("human", bid)
        game.next_turn()

        print("Your bid:", display_bid(bid))

    else:

        result = game.call_bullshit("human")

        print("\n=== CHALLENGE RESULT ===")
        print("Claim:", display_bid(result.bid))
        print("Claim was:", "TRUE" if result.claim_is_true else "FALSE")
        print("Loser:", game.get_player(result.loser_id).name)


def display_game(game):

    print("\n" + format_table(game.players, "human"))

    print(f"\nRound: {game.round_number}")

    if game.bid_manager.current_bid is not None:
        print(
            "Current claim:",
            display_bid(game.bid_manager.current_bid)
        )


def run_game(input_fn=input):

    print("=" * 40)
    print("          LIAR'S POKER")
    print("=" * 40)

    players, bots = create_players(input_fn)

    game = GameState(players, bots=bots)
    game.start_game()

    while not game.finished:

        if game.round_resolved:

            print("\nStarting next round...")

            game.start_next_round()
            continue

        display_game(game)

        current_player = game.current_player

        if current_player.player_id == "human":

            play_human_turn(game, input_fn)

        else:

            bot = game.bots[current_player.player_id]

            print("\n" + "=" * 40)
            print(f"BOT DECISION: {bot.name}")
            print(f"Personality: {bot.personality.value}")

            current_bid = game.bid_manager.current_bid

            if current_bid is not None:
                print(f"Evaluating claim: {display_bid(current_bid)}")

            action, result = game.process_bot_turn()

            if bot.last_claim_probability is not None:
                print(
                    f"Estimated claim probability: "
                    f"{bot.last_claim_probability:.1%}"
                )
                print(
                    f"Challenge threshold: "
                    f"{bot.last_challenge_threshold:.1%}"
                )

            print(f"Decision: {action.upper()}")
            print("=" * 40)

            if action == "bid":
                print(f"{bot.name} bids: {display_bid(result)}")

            else:
                print(f"{bot.name} calls BULLSHIT!")
                print(
                    "Claim was:",
                    "TRUE" if result.claim_is_true else "FALSE"
                )
                print(
                    "Loser:",
                    game.get_player(result.loser_id).name
                )

    print("\n" + "=" * 40)
    print("             GAME OVER")
    print("=" * 40)

    if game.winner:
        print(f"Winner: {game.winner.name}")

    return game


if __name__ == "__main__":
    run_game()
