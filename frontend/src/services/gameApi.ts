
const API_BASE_URL = 'http://127.0.0.1:8000'

// --------------------------------------------------
// TYPES — Match the FastAPI response models
// --------------------------------------------------

export type CardData = {
  rank: string
  rank_value: number
  suit: string
}

export type PlayerData = {
  player_id: string
  name: string
  is_human: boolean
  is_bot: boolean
  personality: string | null
  cards: CardData[]
  card_count: number
  hand_size: number
  eliminated: boolean
}

export type BidData = {
  category: string
  values: (number | string)[]
  description: string
}

export type ActivityData = {
  player: string
  action: string
  description: string
  probability?: number
  claim_is_true?: boolean
  loser_id?: string
}

export type GameState = {
  game_id: string
  round_number: number
  players: PlayerData[]
  current_player_id: string | null
  current_bid: BidData | null
  bidder_id: string | null
  round_resolved: boolean
  finished: boolean
  winner: {
    player_id: string
    name: string
  } | null
  cards_revealed: boolean
  activity: ActivityData[]
}

export type CreateGameRequest = {
  player_name: string
  bot_personalities: (
    | 'Conservative'
    | 'Aggressive'
    | 'Detective'
  )[]
}

export type PlaceBidRequest = {
  category: string
  values: (number | string)[]
}

export type ChallengeResponse = {
  game: GameState
  challenge_result: {
    bid: string
    claim_is_true: boolean
    bidder_id: string
    challenger_id: string
    loser_id: string
    loser_name: string
  }
}


// --------------------------------------------------
// HTTP HELPER
// --------------------------------------------------

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.detail ?? 'Something went wrong while communicating with the server.',
    )
  }

  return data as T
}


// --------------------------------------------------
// API FUNCTIONS
// --------------------------------------------------

export function createGame(
  payload: CreateGameRequest,
): Promise<GameState> {
  return request<GameState>('/games', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getGameState(
  gameId: string,
): Promise<GameState> {
  return request<GameState>(`/games/${gameId}`)
}

export function placeBid(
  gameId: string,
  payload: PlaceBidRequest,
): Promise<GameState> {
  return request<GameState>(`/games/${gameId}/bid`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function callBullshit(
  gameId: string,
): Promise<ChallengeResponse> {
  return request<ChallengeResponse>(
    `/games/${gameId}/challenge`,
    {
      method: 'POST',
    },
  )
}

export function startNextRound(
  gameId: string,
): Promise<GameState> {
  return request<GameState>(
    `/games/${gameId}/next-round`,
    {
      method: 'POST',
    },
  )
}
