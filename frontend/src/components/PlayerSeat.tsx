
import { Crown } from 'lucide-react'
import PlayingCard from './PlayingCard'

type PlayerSeatProps = {
  name: string
  cards: number
  isActive?: boolean
  isYou?: boolean
}

function PlayerSeat({
  name,
  cards,
  isActive = false,
  isYou = false,
}: PlayerSeatProps) {
  return (
    <div className={`flex flex-col items-center gap-2 ${
      isActive ? 'scale-105' : ''
    } transition-transform`}>
      <div className={`relative w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold border-2 ${
        isActive
          ? 'border-amber-400 bg-amber-400/15 text-amber-300'
          : 'border-white/15 bg-[#26352c] text-gray-300'
      }`}>
        {name.charAt(0).toUpperCase()}

        {isActive && (
          <span className="absolute -top-2 -right-2 text-amber-400">
            <Crown size={16} />
          </span>
        )}
      </div>

      <div className="text-center">
        <p className="text-sm font-semibold text-white">
          {name} {isYou && '(You)'}
        </p>
        <p className="text-xs text-gray-400">
          {cards} cards
        </p>
      </div>

      <div className="flex -space-x-5">
        {Array.from({ length: cards }).map((_, index) => (
          <div key={index} className="scale-75 origin-top">
            <PlayingCard hidden />
          </div>
        ))}
      </div>
    </div>
  )
}

export default PlayerSeat
