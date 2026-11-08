
import { useState } from 'react'
import {
  Crown,
  Coins,
  Clock3,
  History,
  CircleHelp,
  Sparkles,
  Play,
  RefreshCw,
} from 'lucide-react'

import PlayingCard from './components/PlayingCard'
import PlayerSeat from './components/PlayerSeat'

import {
  createGame,
  type GameState,
  type CardData,
} from './services/gameApi'

import BidBuilder, { type BidPayload } from './BidBuilder'

import {
  placeBid,
  callBullshit,
  startNextRound,
  type ChallengeResponse,
} from './services/gameApi'


const BOT_PERSONALITIES = [
  'Conservative',
  'Aggressive',
  'Detective',
] as const


function getRankLabel(rank: string) {
  const labels: Record<string, string> = {
    JACK: 'J',
    QUEEN: 'Q',
    KING: 'K',
    ACE: 'A',
  }

  return labels[rank] ?? rank
}


function getSuitSymbol(suit: string) {
  const symbols: Record<string, string> = {
    Hearts: '♥',
    Diamonds: '♦',
    Clubs: '♣',
    Spades: '♠',
  }

  return symbols[suit] ?? suit
}


function App() {
  const [game, setGame] = useState<GameState | null>(null)
  const [playerName, setPlayerName] = useState('You')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [actionLoading, setActionLoading] = useState(false)
  const [challengeResult, setChallengeResult] =
    useState<ChallengeResponse['challenge_result'] | null>(null)

  const handleStartGame = async () => {
    setLoading(true)
    setError('')

    try {
      const newGame = await createGame({
        player_name: playerName.trim() || 'You',
        bot_personalities: [...BOT_PERSONALITIES],
      })

      setGame(newGame)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Could not create the game.',
      )
    } finally {
      setLoading(false)
    }
  }

  const handleRaise = async (bid: BidPayload) => {
    if (!game) return

    setActionLoading(true)
    setError('')
    setChallengeResult(null)

    try {
      const updatedGame = await placeBid(game.game_id, bid)
      setGame(updatedGame)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Could not place bid.',
      )
    } finally {
      setActionLoading(false)
    }
  }

  const handleChallenge = async () => {
    if (!game) return

    setActionLoading(true)
    setError('')

    try {
      const response = await callBullshit(game.game_id)

      setGame(response.game)
      setChallengeResult(response.challenge_result)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Challenge failed.',
      )
    } finally {
      setActionLoading(false)
    }
  }

  const handleNextRound = async () => {
    if (!game) return

    setActionLoading(true)
    setError('')
    setChallengeResult(null)

    try {
      const updatedGame = await startNextRound(game.game_id)
      setGame(updatedGame)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Could not start next round.',
      )
    } finally {
      setActionLoading(false)
    }
  }

  const human = game?.players.find((player) => player.is_human)

  const bots = game?.players.filter((player) => player.is_bot) ?? []

  const topPlayer = bots[0]
  const leftPlayer = bots[1]
  const rightPlayer = bots[2]

  const currentPlayer = game?.players.find(
    (player) => player.player_id === game.current_player_id,
  )

  // Get the latest two bids from the activity history.
  const activity = game?.activity ?? []

  // Find the most recent challenge. Everything before it
  // belongs to an earlier round.
  const lastChallengeIndex = activity.map(
    (entry) => entry.action,
  ).lastIndexOf('challenge')

  // Keep only bids from the current round.
  const currentRoundActivity = activity.slice(lastChallengeIndex + 1)

  const bidHistory = currentRoundActivity.filter(
    (entry) => entry.action === 'bid',
  )

  const latestBid = bidHistory[bidHistory.length - 1]
  const previousBid = bidHistory[bidHistory.length - 2]

  const latestBidPlayer = game?.players.find(
    (player) => player.name === latestBid?.player,
  )

  const isHumanTurn = game?.current_player_id === 'human'

  const canPlay =
    !!game &&
    isHumanTurn &&
    !game.round_resolved &&
    !game.finished &&
    !actionLoading

  const renderPlayer = (
    player: typeof topPlayer,
    position: string,
  ) => {
    if (!player) return null

    return (
      <div className={`table-seat ${position}`}>
        <PlayerSeat
          name={player.name}
          cards={player.card_count}
          cardData={player.cards}
          isActive={player.player_id === game?.current_player_id}
          isEliminated={player.eliminated}
          revealCards={game?.cards_revealed ?? false}
        />
      </div>
    )
  }

  return (
    <main className="app-shell min-h-screen bg-[#101713] text-white">

      {/* Header */}
      <header className="app-header min-h-20 border-b border-white/10 px-4 sm:px-6 lg:px-10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center">
            <Crown className="text-emerald-400" size={22} />
          </div>

          <div>
            <h1 className="font-bold tracking-wide text-lg">
              LIAR'S <span className="text-emerald-400">POKER</span>
            </h1>
            <p className="text-xs text-gray-500 tracking-widest">
              THE ART OF DECEPTION
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-sm text-gray-400">
          <Coins size={17} className="text-amber-400" />
          Practice Match
        </div>
      </header>

      <div className="max-w-[1500px] mx-auto p-3 sm:p-5 lg:p-8 grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_300px] gap-5 lg:gap-6">

        {/* Game area */}
        <section className="min-w-0">

          <div className="flex justify-between items-center mb-5">
            <div>
              <p className="text-xs tracking-widest text-gray-500">
                GAME ROOM
              </p>
              <h2 className="text-xl font-semibold mt-1">
                The Green Table
              </h2>
            </div>

            <div className="flex items-center gap-2 text-xs text-gray-400 bg-white/5 border border-white/10 px-3 py-2 rounded-lg">
              <Clock3 size={14} />
              ROUND {String(game?.round_number ?? 0).padStart(2, '0')}
            </div>
          </div>

          {/* Poker table */}
          <div className="relative table-felt relative min-h-[550px] lg:min-h-[620px] rounded-[28px] sm:rounded-[40px] border-[10px] border-[#493b26] bg-[#164a34] shadow-[inset_0_0_80px_rgba(0,0,0,0.45),0_20px_60px_rgba(0,0,0,0.3)] overflow-hidden">

            <div className="absolute inset-3 rounded-[32px] border border-white/10 pointer-events-none" />

            <div
              className="absolute inset-0 opacity-10 pointer-events-none"
              style={{
                backgroundImage: 'radial-gradient(#ffffff 0.7px, transparent 0.7px)',
                backgroundSize: '8px 8px',
              }}
            />

            {game && (
              <>
                {renderPlayer(
                  topPlayer,
                  'table-top absolute top-5 left-1/2 -translate-x-1/2',
                )}

                {renderPlayer(
                  leftPlayer,
                  'table-left absolute left-4 lg:left-10 top-1/2 -translate-y-1/2',
                )}

                {renderPlayer(
                  rightPlayer,
                  'table-right absolute right-4 lg:right-10 top-1/2 -translate-y-1/2',
                )}

                {/* Center area */}     
                {/* Live Bid Display */}
                <div className="table-center absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[52%] max-w-[560px] text-center">

                  <p className="text-emerald-200/50 text-[10px] tracking-[0.25em] mb-2">
                    LIVE BID
                  </p>

                  <div className="bg-black/25 border border-amber-400/20 rounded-xl px-4 py-3 backdrop-blur-sm">

                    {latestBid ? (
                      <>
                        <div className="flex justify-between items-center gap-2">
                          <div className="text-left min-w-0">
                            <p className="text-emerald-200/70 text-[10px] font-semibold truncate">
                              {latestBid.player.toUpperCase()}
                            </p>

                            {latestBidPlayer?.personality && (
                              <p className="text-emerald-100/40 text-[9px] mt-0.5">
                                {latestBidPlayer.personality} Bot
                              </p>
                            )}
                          </div>

                          <span className="text-[9px] text-amber-300 bg-amber-400/10 px-2 py-1 rounded-full shrink-0">
                            LATEST
                          </span>
                        </div>

                        <p className="text-xl lg:text-2xl font-bold text-amber-300 mt-2 break-words">
                          {latestBid.description}
                        </p>

                        {typeof latestBid.probability === 'number' && (
                          <div className="mt-2">
                            <div className="flex justify-between text-[10px] text-emerald-100/50">
                              <span>Estimated probability</span>
                              <span className="text-white font-semibold">
                                {(latestBid.probability * 100).toFixed(1)}%
                              </span>
                            </div>

                            <div className="w-full h-1 bg-white/10 rounded-full mt-1 overflow-hidden">
                              <div
                                className="h-full bg-emerald-400 rounded-full"
                                style={{
                                  width: `${Math.max(0, Math.min(100, latestBid.probability * 100))}%`,
                                }}
                              />
                            </div>
                          </div>
                        )}

                        {previousBid && (
                          <div className="mt-3 pt-2 border-t border-white/10 text-left">
                            <p className="text-[9px] tracking-widest text-emerald-100/40">
                              PREVIOUS BID
                            </p>
                            <p className="text-[11px] text-gray-300 mt-1 truncate">
                              {previousBid.player} · {previousBid.description}
                            </p>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="py-2">
                        <p className="text-xl font-bold text-amber-300">
                          No bids yet
                        </p>
                        <p className="text-[10px] text-emerald-100/50 mt-1">
                          Waiting for the opening bid
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="flex justify-center items-center gap-2 mt-2">
                    <span className={`w-1.5 h-1.5 rounded-full ${actionLoading ? "bg-amber-300" : "bg-emerald-400"} animate-pulse`} />

                    <p className="text-[10px] text-emerald-100/70">
                      {actionLoading
                        ? 'Processing move…'
                        : game.round_resolved
                        ? 'Round resolved'
                        : currentPlayer
                          ? currentPlayer.is_human
                            ? "It's your turn!"
                            : `${currentPlayer.name} is playing`
                          : 'Waiting'}
                    </p>
                  </div>

                </div>



                {/* Human position */}
                <div className="table-seat table-human absolute bottom-5 left-1/2 -translate-x-1/2">
                  <PlayerSeat
                    name={human?.name ?? 'You'}
                    cards={human?.card_count ?? 0}
                    isYou
                    isActive={game.current_player_id === 'human'}
                    isEliminated={human?.eliminated ?? false}
                    cardData={human?.cards}
                    revealCards={game.cards_revealed}
                  />
                </div>
              </>
            )}

            {!game && (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
                <Crown size={42} className="text-emerald-400 mb-4" />
                <h3 className="text-2xl font-bold">The table is waiting</h3>
                <p className="text-sm text-emerald-100/60 mt-2">
                  Start a match to take your seat.
                </p>
              </div>
            )}
          </div>

          {/* Human hand */}
          {game && (
            <div className="mt-7 flex flex-col items-center">
              <p className="text-xs text-gray-500 tracking-[0.25em] mb-4">
                YOUR HAND
              </p>

              <div className="flex gap-4">
                {human?.cards.map((card: CardData, index) => (
                  <PlayingCard
                    key={`${card.rank}-${card.suit}-${index}`}
                    rank={getRankLabel(card.rank)}
                    suit={getSuitSymbol(card.suit)}
                  />
                ))}
              </div>
            </div>
          )}


          {/* Game actions */}
          {game && (
            <div className="mt-7 max-w-xl mx-auto space-y-4">

              {!game.round_resolved && !game.finished && (
                <>
                  <BidBuilder
                    onSubmit={handleRaise}
                    disabled={!canPlay}
                  />

                  <button
                    onClick={handleChallenge}
                    disabled={!canPlay || !game.current_bid}
                    className="w-full flex items-center justify-center gap-2 bg-red-500/10 border border-red-500/30 hover:bg-red-500/20 disabled:opacity-40 disabled:cursor-not-allowed text-red-300 font-bold py-4 rounded-xl transition-colors"
                  >
                    Bullshit!
                  </button>
                </>
              )}

              {game.round_resolved && !game.finished && (
                <div className="bg-[#19251e] border border-amber-500/30 rounded-2xl p-5 text-center">
                  <h3 className="text-lg font-bold text-amber-300">
                    Round Complete!
                  </h3>

                  <p className="text-sm text-gray-400 mt-2">
                    {challengeResult
                      ? `${challengeResult.loser_name} lost the challenge.`
                      : 'The challenge has been resolved.'}
                  </p>

                  <button
                    onClick={handleNextRound}
                    disabled={actionLoading}
                    className="mt-5 w-full bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-[#0c1b13] font-bold py-3 rounded-xl"
                  >
                    {actionLoading ? 'Starting...' : 'Start Next Round'}
                  </button>
                </div>
              )}

              {game.finished && (
                <div className="bg-[#19251e] border border-emerald-500/30 rounded-2xl p-5 text-center">
                  <h3 className="text-xl font-bold text-emerald-400">
                    Game Over!
                  </h3>
                  <p className="text-gray-300 mt-2">
                    Winner: {game.winner?.name ?? 'Unknown'}
                  </p>
                </div>
              )}

            </div>
          )}

          {/* Start game */}
          {!game && (
            <div className="landing-panel mt-7 max-w-2xl mx-auto rounded-3xl border border-emerald-400/20 bg-gradient-to-br from-[#1b3025] to-[#17221b] p-6 sm:p-9">
              <div className="flex items-center gap-2 text-emerald-300 text-xs tracking-[0.25em] font-semibold">
                <Sparkles size={15} /> THE TABLE IS YOURS
              </div>
              <h2 className="mt-4 text-3xl sm:text-4xl font-black tracking-tight">
                Bluff your way to <span className="text-amber-300">victory.</span>
              </h2>
              <p className="mt-3 max-w-xl text-sm sm:text-base leading-relaxed text-emerald-100/65">
                Read the table, make your claims, and decide when someone is pushing their luck.
                Three bots. One table. No room for hesitation.
              </p>
              <label className="block mt-7">
                <span className="block text-xs uppercase tracking-widest text-emerald-100/55 mb-2">Your table name</span>
                <input
                  value={playerName}
                  onChange={(event) => setPlayerName(event.target.value)}
                  maxLength={24}
                  placeholder="Enter your name"
                  className="w-full sm:max-w-sm rounded-xl border border-white/10 bg-[#101713]/80 px-4 py-3 text-white outline-none transition focus:border-emerald-400"
                />
              </label>
              <button
                onClick={handleStartGame}
                disabled={loading}
                className="mt-5 w-full sm:w-auto min-w-52 flex items-center justify-center gap-2 bg-emerald-400 hover:bg-emerald-300 disabled:opacity-50 text-[#0c1b13] font-bold px-7 py-4 rounded-xl transition-all hover:-translate-y-0.5"
              >
                {loading ? <RefreshCw size={18} className="animate-spin" /> : <Play size={18} />}
                {loading ? 'Preparing the table…' : 'Enter the table'}
              </button>
              <p className="mt-4 text-[11px] text-emerald-100/35">Practice match · 4 players · Against AI opponents</p>
            </div>
          )}

          {error && (
            <p className="text-center text-sm text-red-400 mt-4">
              {error}
            </p>
          )}

          {challengeResult && (
            <div
              className={`mt-5 rounded-2xl border p-5 text-center ${
                challengeResult.claim_is_true
                  ? 'bg-red-500/10 border-red-500/30'
                  : 'bg-emerald-500/10 border-emerald-500/30'
              }`}
            >
              <div className="text-3xl mb-2">
                {challengeResult.claim_is_true ? '⚠️' : '🎉'}
              </div>

              <p className={`text-xl font-bold ${
                challengeResult.claim_is_true
                  ? 'text-red-300'
                  : 'text-emerald-300'
              }`}>
                {challengeResult.claim_is_true
                  ? 'The Claim Was TRUE!'
                  : 'The Claim Was FALSE!'}
              </p>

              <p className="text-sm text-gray-300 mt-3">
                {challengeResult.bidder_id === 'human'
                  ? 'You'
                  : game?.players.find(
                      (player) => player.player_id === challengeResult.bidder_id,
                    )?.name ?? 'The bidder'} 
                {' '}claimed:
              </p>

              <p className="text-amber-300 font-semibold mt-1">
                {challengeResult.bid}
              </p>

              <div className="mt-4 pt-4 border-t border-white/10">
                <p className="text-xs text-gray-400">CHALLENGE LOSER</p>

                <p className="text-lg font-bold text-white mt-1">
                  {challengeResult.loser_name}
                </p>

                <p className="text-xs text-gray-400 mt-1">
                  {challengeResult.loser_id === 'human'
                    ? 'You will receive a penalty card.'
                    : 'This player will receive a penalty card.'}
                </p>
              </div>
            </div>
          )}


        </section>

        {/* Sidebar */}
        <aside className="space-y-5">

          <div className="bg-[#19251e] border border-white/10 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-5">
              <Sparkles className="text-amber-400" size={18} />
              <h3 className="font-semibold">Match Overview</h3>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Players</span>
                <span>{game ? game.players.length : '—'} / 8</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Round</span>
                <span>{game?.round_number ?? '—'}</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Your cards</span>
                <span>{human?.card_count ?? '—'}</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Status</span>
                <span className="text-emerald-400">
                  {game
                    ? game.finished
                      ? 'Finished'
                      : game.round_resolved
                        ? 'Round Resolved'
                        : 'In Progress'
                    : 'Not Started'}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-[#19251e] border border-white/10 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <History className="text-emerald-400" size={18} />
              <h3 className="font-semibold">Activity Log</h3>
            </div>

            <div className="activity-list space-y-4 text-sm max-h-[520px] overflow-y-auto pr-1">
              {game?.activity.length ? (
                game.activity.slice().reverse().map((entry, index) => (
                  <div
                    key={`${entry.player}-${index}`}
                    className="border-l-2 border-emerald-500/50 pl-3"
                  >
                    <p className="text-gray-300">
                      {entry.player}
                      {' '}
                      {entry.action === 'bid'
                        ? 'made a bid'
                        : 'called Bullshit'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {entry.description}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-sm">
                  {game ? 'Waiting for the first move...' : 'No match started yet.'}
                </p>
              )}
            </div>
          </div>

          <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <CircleHelp size={18} className="text-emerald-400" />
              <h3 className="font-semibold text-sm">How to play</h3>
            </div>

            <p className="text-xs text-gray-400 leading-relaxed">
              Raise the current poker claim or call Bullshit if you believe
              the previous player's claim is false. Be careful — a failed
              challenge costs you a card!
            </p>
          </div>

        </aside>
      </div>
    </main>
  )
}

export default App
