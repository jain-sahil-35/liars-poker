from enum import Enum
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from game.player import Player
from game.game_state import GameState
from game.bot import Bot, BotPersonality
from game.bidding import Bid
from game.cards import Card, Rank, Suit
from game.hand_evaluator import HandRank


app = FastAPI(
    title="Liar's Poker API",
    description="Backend API for the Liar's Poker game.",
    version="1.0.0",
)


# Allow the React development server to communicate with this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Temporary in-memory storage.
# Games will disappear when the server restarts.
games: dict[str, GameState] = {}

# Store bot activity separately from the game engine.
game_activity: dict[str, list[dict]] = {}


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class CreateGameRequest(BaseModel):
    player_name: str = Field(default="You", min_length=1, max_length=30)

    bot_personalities: list[BotPersonality] = Field(
        default=[
            BotPersonality.CONSERVATIVE,
            BotPersonality.AGGRESSIVE,
            BotPersonality.DETECTIVE,
        ],
        min_length=1,
        max_length=7,
    )


class PlaceBidRequest(BaseModel):
    category: str
    values: list[int | str]


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_game(game_id: str) -> GameState:
    """Retrieve a game or raise a 404 error."""

    game = games.get(game_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    return game


def serialize_card(card: Card) -> dict:
    return {
        "rank": card.rank.name,
        "rank_value": int(card.rank),
        "suit": card.suit.value,
    }


def serialize_bid(bid: Bid | None) -> dict | None:
    if bid is None:
        return None

    values = []

    for value in bid.values:
        if isinstance(value, Enum):
            values.append(value.value)
        else:
            values.append(value)

    return {
        "category": bid.category.name,
        "values": values,
        "description": str(bid),
    }


def serialize_game(game_id: str, game: GameState) -> dict:
    """Create a frontend-safe representation of the game."""

    reveal_cards = game.round_resolved or game.finished

    players = []

    for player in game.players:
        is_human = player.player_id == "human"

        # The human sees their own cards.
        # Everyone's cards become visible after a challenge.
        visible_cards = (
            player.cards
            if is_human or reveal_cards
            else []
        )

        players.append({
            "player_id": player.player_id,
            "name": player.name,
            "is_human": is_human,
            "is_bot": player.player_id in game.bots,
            "personality": (
                game.bots[player.player_id].personality.value
                if player.player_id in game.bots
                else None
            ),
            "cards": [
                serialize_card(card)
                for card in visible_cards
            ],
            "card_count": player.card_count,
            "hand_size": player.hand_size,
            "eliminated": player.eliminated,
        })

    current_player = game.current_player

    return {
        "game_id": game_id,
        "round_number": game.round_number,
        "players": players,
        "current_player_id": (
            current_player.player_id
            if current_player else None
        ),
        "current_bid": serialize_bid(
            game.bid_manager.current_bid
        ),
        "bidder_id": game.bidder_id,
        "round_resolved": game.round_resolved,
        "finished": game.finished,
        "winner": (
            {
                "player_id": game.winner.player_id,
                "name": game.winner.name,
            }
            if game.winner else None
        ),
        "cards_revealed": reveal_cards,
        "activity": game_activity[game_id],
    }


def create_bid(request: PlaceBidRequest) -> Bid:
    """Convert frontend bid data into a validated Bid object."""

    try:
        category = HandRank[request.category.upper()]
        values = request.values

        if category == HandRank.FLUSH:
            suit = Suit(values[0])
            rank = Rank(int(values[1]))
            bid_values = (suit, rank)

        elif category == HandRank.STRAIGHT_FLUSH:
            suit = Suit(values[0])
            high_rank = int(values[1])
            bid_values = (suit, high_rank)

        elif category == HandRank.ROYAL_FLUSH:
            suit = Suit(values[0])
            bid_values = (suit,)

        else:
            bid_values = tuple(int(value) for value in values)

        return Bid(category, bid_values)

    except (KeyError, ValueError, TypeError, IndexError) as error:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid bid: {error}",
        )



# --------------------------------------------------
# ROUTES
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to the Liar's Poker API!",
        "docs": "/docs",
    }


@app.post("/games")
def create_game(request: CreateGameRequest):
    """Create a new game and deal the first round."""

    game_id = str(uuid4())

    human = Player(
        player_id="human",
        name=request.player_name.strip(),
    )

    players = [human]
    bots = {}

    for index, personality in enumerate(
        request.bot_personalities,
        start=1,
    ):
        player_id = f"bot_{index}"

        player = Player(
            player_id=player_id,
            name=f"Bot {index}",
        )

        players.append(player)

        bots[player_id] = Bot(
            player=player,
            personality=personality,
        )

    try:
        game = GameState(players, bots=bots)
        game.start_game()

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    games[game_id] = game
    game_activity[game_id] = []

    return serialize_game(game_id, game)


@app.get("/games/{game_id}")
def get_game_state(game_id: str):
    """Return the current game state."""

    game = get_game(game_id)

    return serialize_game(game_id, game)


@app.post("/games/{game_id}/bid")
def place_bid(game_id: str, request: PlaceBidRequest):
    """Accept a human bid. Bot turns are advanced separately by the frontend."""

    game = get_game(game_id)

    if game.finished or game.round_resolved:
        raise HTTPException(
            status_code=400,
            detail="This round is not accepting bids.",
        )

    if game.current_player.player_id != "human":
        raise HTTPException(
            status_code=400,
            detail="It is not your turn.",
        )

    bid = create_bid(request)

    try:
        game.place_bid("human", bid)
        game.next_turn()

        game_activity[game_id].append({
            "player": game.get_player("human").name,
            "action": "bid",
            "description": str(bid),
        })


    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    return serialize_game(game_id, game)


@app.post("/games/{game_id}/advance-bot")
def advance_bot(game_id: str):
    """Execute exactly one bot action and return the updated game state."""

    game = get_game(game_id)

    if game.finished or game.round_resolved:
        raise HTTPException(
            status_code=400,
            detail="The round is not accepting bot actions.",
        )

    current_player = game.current_player

    if current_player is None or current_player.player_id == "human":
        raise HTTPException(
            status_code=400,
            detail="It is not a bot's turn.",
        )

    bot = game.bots.get(current_player.player_id)

    if bot is None:
        raise HTTPException(
            status_code=400,
            detail="The current player is not a registered bot.",
        )

    try:
        action, result = game.process_bot_turn()
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if action == "bid":
        game_activity[game_id].append({
            "player": bot.name,
            "action": "bid",
            "description": str(result),
            "probability": bot.last_bid_probability,
        })
    elif action == "challenge":
        game_activity[game_id].append({
            "player": bot.name,
            "action": "challenge",
            "description": "Called Bullshit!",
            "claim_is_true": result.claim_is_true,
            "loser_id": result.loser_id,
        })

    return serialize_game(game_id, game)


@app.post("/games/{game_id}/challenge")
def call_bullshit(game_id: str):
    """Challenge the current bid."""

    game = get_game(game_id)

    if game.finished or game.round_resolved:
        raise HTTPException(
            status_code=400,
            detail="This round has already been resolved.",
        )

    if game.current_player.player_id != "human":
        raise HTTPException(
            status_code=400,
            detail="It is not your turn.",
        )

    try:
        result = game.call_bullshit("human")

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    game_activity[game_id].append({
        "player": game.get_player("human").name,
        "action": "challenge",
        "description": "Called Bullshit!",
        "claim_is_true": result.claim_is_true,
        "loser_id": result.loser_id,
    })

    return {
        "game": serialize_game(game_id, game),
        "challenge_result": {
            "bid": str(result.bid),
            "claim_is_true": result.claim_is_true,
            "bidder_id": result.bidder_id,
            "challenger_id": result.challenger_id,
            "loser_id": result.loser_id,
            "loser_name": game.get_player(result.loser_id).name,
        },
    }


@app.post("/games/{game_id}/next-round")
def start_next_round(game_id: str):
    """Start the next round after a resolved challenge."""

    game = get_game(game_id)

    if game.finished:
        raise HTTPException(
            status_code=400,
            detail="The game has finished.",
        )

    try:
        game.start_next_round()


    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    return serialize_game(game_id, game)