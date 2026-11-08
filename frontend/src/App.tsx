
import { useState } from 'react'
import {
  ArrowUp,
  CircleHelp,
  Clock3,
  Coins,
  Crown,
  History,
  Settings,
  ShieldAlert,
  Sparkles,
} from 'lucide-react'

import BidBuilder, { type BidPayload } from './BidBuilder'

import PlayingCard from './components/PlayingCard'
import PlayerSeat from './components/PlayerSeat'

const initialPlayers = [
  { name: 'Alex', cards: 2, position: 'top' },
  { name: 'Nova', cards: 3, position: 'left' },
  { name: 'You', cards: 2, position: 'bottom' },
  { name: 'Shadow', cards: 2, position: 'right' },
]

function App() {
  const [currentBid, setCurrentBid] = useState('Pair of Kings')
  const [activity, setActivity] = useState('Waiting for your move...')

  const handleRaise = (bid: BidPayload) => {
    const rankNames: Record<number, string> = {
      2: '2',
      3: '3',
      4: '4',
      5: '5',
      6: '6',
      7: '7',
      8: '8',
      9: '9',
      10: '10',
      11: 'Jack',
      12: 'Queen',
      13: 'King',
      14: 'Ace',
    }

    const categoryNames: Record<BidPayload['category'], string> = {
      HIGH_CARD: 'High Card',
      ONE_PAIR: 'One Pair',
      TWO_PAIR: 'Two Pair',
      THREE_OF_A_KIND: 'Three of a Kind',
      STRAIGHT: 'Straight',
      FLUSH: 'Flush',
      FULL_HOUSE: 'Full House',
      FOUR_OF_A_KIND: 'Four of a Kind',
      STRAIGHT_FLUSH: 'Straight Flush',
      ROYAL_FLUSH: 'Royal Flush',
    }

    const formattedValues = bid.values.map((value) =>
      typeof value === 'number' ? rankNames[value] : value
    )

    const bidDescription = [
      categoryNames[bid.category],
      ...formattedValues,
    ].join(' - ')

    setCurrentBid(bidDescription)
    setActivity('You raised the bid.')
  }

  const handleChallenge = () => {
    setActivity('You called Bullshit! Challenge simulation pending.')
  }

  return (
    <main className="min-h-screen bg-[#101713] text-white">
      {/* Header */}
      <header className="h-20 border-b border-white/10 px-6 lg:px-10 flex items-center justify-between">
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

        <div className="flex items-center gap-5">
          <div className="hidden sm:flex items-center gap-2 text-sm text-gray-400">
            <Coins size={17} className="text-amber-400" />
            Practice Match
          </div>

          <button className="p-2 rounded-lg hover:bg-white/10 text-gray-400">
            <Settings size={20} />
          </button>
        </div>
      </header>

      <div className="max-w-[1500px] mx-auto p-5 lg:p-8 grid grid-cols-1 xl:grid-cols-[1fr_300px] gap-6">

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
              ROUND 01
            </div>
          </div>

          {/* Poker table */}
          <div className="relative min-h-[550px] lg:min-h-[620px] rounded-[40px] border-[10px] border-[#493b26] bg-[#164a34] shadow-[inset_0_0_80px_rgba(0,0,0,0.45),0_20px_60px_rgba(0,0,0,0.3)] overflow-hidden">

            <div className="absolute inset-3 rounded-[32px] border border-white/10 pointer-events-none" />

            {/* Table texture */}
            <div className="absolute inset-0 opacity-10 pointer-events-none"
              style={{
                backgroundImage: 'radial-gradient(#ffffff 0.7px, transparent 0.7px)',
                backgroundSize: '8px 8px',
              }}
            />

            {/* Player positions */}
            <div className="absolute top-5 left-1/2 -translate-x-1/2">
              <PlayerSeat name="Alex" cards={2} />
            </div>

            <div className="absolute left-4 lg:left-10 top-1/2 -translate-y-1/2">
              <PlayerSeat name="Nova" cards={3} isActive />
            </div>

            <div className="absolute right-4 lg:right-10 top-1/2 -translate-y-1/2">
              <PlayerSeat name="Shadow" cards={2} />
            </div>

            {/* Center area */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[55%] text-center">
              <p className="text-emerald-200/50 text-xs tracking-[0.3em] mb-3">
                CURRENT BID
              </p>

              <div className="bg-black/20 border border-white/10 rounded-2xl p-5 backdrop-blur-sm">
                <p className="text-2xl lg:text-3xl font-bold text-amber-300">
                  {currentBid}
                </p>
                <p className="text-xs text-emerald-100/50 mt-2">
                  Last bidder: Nova
                </p>
              </div>

              <div className="flex justify-center items-center gap-2 mt-5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <p className="text-xs text-emerald-100/70">
                  Nova's turn completed
                </p>
              </div>
            </div>

            {/* Your position */}
            <div className="absolute bottom-5 left-1/2 -translate-x-1/2 flex flex-col items-center">
              <PlayerSeat name="You" cards={2} isYou />
            </div>
          </div>

          {/* Your cards */}
          <div className="mt-7 flex flex-col items-center">
            <p className="text-xs text-gray-500 tracking-[0.25em] mb-4">
              YOUR HAND
            </p>

            <div className="flex gap-4">
              <PlayingCard rank="K" suit="♠" />
              <PlayingCard rank="7" suit="♥" />
            </div>
          </div>

          {/* Bid Builder and Game Actions */}
          <div className="mt-7 max-w-xl mx-auto space-y-4">
            <BidBuilder onSubmit={handleRaise} />

            <button
              onClick={handleChallenge}
              className="w-full flex items-center justify-center gap-2 bg-red-500/10 border border-red-500/30 hover:bg-red-500/20 text-red-300 font-bold py-4 rounded-xl transition-colors"
            >
              <ShieldAlert size={18} />
              Bullshit!
            </button>
          </div>

          <p className="text-center text-xs text-gray-500 mt-4">
            {activity}
          </p>
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
                <span>4 / 4</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Round</span>
                <span>01</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Your cards</span>
                <span>2</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Status</span>
                <span className="text-emerald-400">In Progress</span>
              </div>
            </div>
          </div>

          <div className="bg-[#19251e] border border-white/10 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <History className="text-emerald-400" size={18} />
              <h3 className="font-semibold">Activity Log</h3>
            </div>

            <div className="space-y-4 text-sm">
              <div>
                <p className="text-gray-300">Nova made a bid</p>
                <p className="text-xs text-gray-500 mt-1">
                  Pair of Kings
                </p>
              </div>

              <div className="border-l-2 border-emerald-500/50 pl-3">
                <p className="text-emerald-300">Your turn</p>
                <p className="text-xs text-gray-500 mt-1">
                  Choose your action
                </p>
              </div>
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
