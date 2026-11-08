
type PlayingCardProps = {
  rank?: string
  suit?: string
  hidden?: boolean
}

function PlayingCard({
  rank,
  suit,
  hidden = false,
}: PlayingCardProps) {
  if (hidden) {
    return (
      <div className="w-12 h-[68px] rounded-lg bg-gradient-to-br from-emerald-800 to-emerald-950 border border-emerald-500/40 p-1 shadow-lg">
        <div className="w-full h-full rounded border border-emerald-400/30 flex items-center justify-center">
          <span className="text-emerald-300 text-xl">♠</span>
        </div>
      </div>
    )
  }

  const isRed = suit === '♥' || suit === '♦'

  return (
    <div className="w-14 h-[78px] rounded-lg bg-[#f5f0df] text-gray-900 shadow-lg p-1.5 flex flex-col justify-between border border-black/10">
      <div>
        <p className={`text-sm font-bold leading-none ${
          isRed ? 'text-red-600' : 'text-gray-900'
        }`}>
          {rank}
        </p>

        <p className={`text-sm leading-none ${
          isRed ? 'text-red-600' : 'text-gray-900'
        }`}>
          {suit}
        </p>
      </div>

      <span className={`text-2xl self-center ${
        isRed ? 'text-red-600' : 'text-gray-900'
      }`}>
        {suit}
      </span>
    </div>
  )
}

export default PlayingCard
