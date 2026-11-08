
import { Crown, Skull } from 'lucide-react'
import PlayingCard from './PlayingCard'

type CardData = {
  rank: string
  rank_value: number
  suit: string
}

type PlayerSeatProps = {
  name: string
  cards: number
  cardData?: CardData[]
  isActive?: boolean
  isYou?: boolean
  isEliminated?: boolean
  revealCards?: boolean
}

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

function PlayerSeat({
  name,
  cards,
  cardData = [],
  isActive = false,
  isYou = false,
  isEliminated = false,
  revealCards = false,
}: PlayerSeatProps) {
  const shouldReveal = revealCards && cardData.length > 0

  return (
    <div
      className={`flex flex-col items-center gap-2 transition-all ${
        isEliminated
          ? 'opacity-40 grayscale'
          : isActive
            ? 'scale-105'
            : ''
      }`}
    >
      {/* Player avatar */}
      <div
        className={`relative w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold border-2 ${
          isEliminated
            ? 'border-red-500/50 bg-red-500/10 text-red-300'
            : isActive
              ? 'border-amber-400 bg-amber-400/15 text-amber-300'
              : 'border-white/15 bg-[#26352c] text-gray-300'
        }`}
      >
        {isEliminated ? (
          <Skull size={20} />
        ) : (
          name.charAt(0).toUpperCase()
        )}

        {isActive && !isEliminated && (
          <span className="absolute -top-2 -right-2 text-amber-400">
            <Crown size={16} />
          </span>
        )}
      </div>

      {/* Player information */}
      <div className="text-center">
        <p className="text-sm font-semibold text-white">
          {name} {isYou && '(You)'}
        </p>

        <p className={`text-xs ${
          isEliminated ? 'text-red-400' : 'text-gray-400'
        }`}>
          {isEliminated ? 'Eliminated' : `${cards} cards`}
        </p>
      </div>

      {/* Cards */}
      <div className="flex justify-center -space-x-5">
        {shouldReveal
          ? cardData.map((card, index) => (
              <div
                key={`${card.rank}-${card.suit}-${index}`}
                className="scale-75 origin-top"
              >
                <PlayingCard
                  rank={getRankLabel(card.rank)}
                  suit={getSuitSymbol(card.suit)}
                />
              </div>
            ))
          : Array.from({ length: cards }).map((_, index) => (
              <div key={index} className="scale-75 origin-top">
                <PlayingCard hidden />
              </div>
            ))}
      </div>
    </div>
  )
}

export default PlayerSeat
