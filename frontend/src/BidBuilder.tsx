
import { useState } from 'react'
import { ArrowUp, ChevronDown } from 'lucide-react'

type BidCategory =
  | 'HIGH_CARD'
  | 'ONE_PAIR'
  | 'TWO_PAIR'
  | 'THREE_OF_A_KIND'
  | 'STRAIGHT'
  | 'FLUSH'
  | 'FULL_HOUSE'
  | 'FOUR_OF_A_KIND'
  | 'STRAIGHT_FLUSH'
  | 'ROYAL_FLUSH'

type Suit = 'Hearts' | 'Diamonds' | 'Clubs' | 'Spades'

export type BidPayload = {
  category: BidCategory
  values: number[] | [Suit] | [Suit, number]
}

type BidBuilderProps = {
  onSubmit: (bid: BidPayload) => void
  disabled?: boolean
}

const categories: { value: BidCategory; label: string }[] = [
  { value: 'HIGH_CARD', label: 'High Card' },
  { value: 'ONE_PAIR', label: 'One Pair' },
  { value: 'TWO_PAIR', label: 'Two Pair' },
  { value: 'THREE_OF_A_KIND', label: 'Three of a Kind' },
  { value: 'STRAIGHT', label: 'Straight' },
  { value: 'FLUSH', label: 'Flush' },
  { value: 'FULL_HOUSE', label: 'Full House' },
  { value: 'FOUR_OF_A_KIND', label: 'Four of a Kind' },
  { value: 'STRAIGHT_FLUSH', label: 'Straight Flush' },
  { value: 'ROYAL_FLUSH', label: 'Royal Flush' },
]

const ranks = [
  { value: 2, label: '2' },
  { value: 3, label: '3' },
  { value: 4, label: '4' },
  { value: 5, label: '5' },
  { value: 6, label: '6' },
  { value: 7, label: '7' },
  { value: 8, label: '8' },
  { value: 9, label: '9' },
  { value: 10, label: '10' },
  { value: 11, label: 'Jack' },
  { value: 12, label: 'Queen' },
  { value: 13, label: 'King' },
  { value: 14, label: 'Ace' },
]

const suits: Suit[] = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

const rankName = (value: number) =>
  ranks.find((rank) => rank.value === value)?.label ?? ''

function BidBuilder({ onSubmit, disabled = false }: BidBuilderProps) {
  const [category, setCategory] = useState<BidCategory>('HIGH_CARD')
  const [rank1, setRank1] = useState(14)
  const [rank2, setRank2] = useState(13)
  const [suit, setSuit] = useState<Suit>('Hearts')

  const needsSuit =
    category === 'FLUSH' ||
    category === 'STRAIGHT_FLUSH' ||
    category === 'ROYAL_FLUSH'
  const needsTwoRanks =
    category === 'TWO_PAIR' || category === 'FULL_HOUSE'

  const isStraight =
    category === 'STRAIGHT' || category === 'STRAIGHT_FLUSH'

  const valid =
    (!isStraight || rank1 >= 6) &&
    (category !== 'STRAIGHT_FLUSH' || rank1 <= 13) &&
    (!needsTwoRanks || rank1 !== rank2) &&
    (category !== 'TWO_PAIR' || rank1 > rank2)

  const createBid = (): BidPayload => {
    if (category === 'ROYAL_FLUSH') {
      return { category, values: [suit] }
    }

    if (category === 'FLUSH' || category === 'STRAIGHT_FLUSH') {
      return { category, values: [suit, rank1] }
    }

    if (category === 'TWO_PAIR') {
      return { category, values: [rank1, rank2] }
    }

    if (category === 'FULL_HOUSE') {
      return { category, values: [rank1, rank2] }
    }

    return { category, values: [rank1] }
  }

  const preview = () => {
    if (category === 'ROYAL_FLUSH') {
      return `Royal Flush – ${suit}`
    }

    if (category === 'FLUSH') {
      return `Flush – ${suit} – ${rankName(rank1)}`
    }

    if (category === 'TWO_PAIR') {
      return `Two Pair – ${rankName(rank1)} and ${rankName(rank2)}`
    }

    if (category === 'FULL_HOUSE') {
      return `Full House – ${rankName(rank1)} over ${rankName(rank2)}`
    }

    if (category === 'STRAIGHT_FLUSH') {
      return `Straight Flush – ${suit} – ${rankName(rank1)} high`
    }

    if (category === 'STRAIGHT') {
      return `Straight – ${rankName(rank1)} high`
    }

    return `${categories.find((item) => item.value === category)?.label} – ${rankName(rank1)}`
  }

  const inputClass =
    'w-full bg-[#101713] border border-white/10 rounded-lg px-3 py-3 text-sm text-white outline-none focus:border-emerald-500'

  return (
    <section className="mt-7 bg-[#19251e] border border-white/10 rounded-2xl p-5 lg:p-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="font-semibold text-lg">Make your bid</h3>
          <p className="text-xs text-gray-500 mt-1">
            Choose a poker claim to challenge the table.
          </p>
        </div>

        <span className="text-xs text-emerald-400 bg-emerald-500/10 px-3 py-2 rounded-lg">
          Bid Builder
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <label className="space-y-2">
          <span className="text-xs text-gray-400">Poker category</span>
          <div className="relative">
            <select
              className={inputClass}
              value={category}
              disabled={disabled}
              onChange={(event) =>
                setCategory(event.target.value as BidCategory)
              }
            >
              {categories.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-3 pointer-events-none text-gray-500" size={17} />
          </div>
        </label>

        {needsSuit && (
          <label className="space-y-2">
            <span className="text-xs text-gray-400">Suit</span>
            <select
              className={inputClass}
              value={suit}
              disabled={disabled}
              onChange={(event) => setSuit(event.target.value as Suit)}
            >
              {suits.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
        )}

        {category !== 'ROYAL_FLUSH' && (
          <label className="space-y-2">
            <span className="text-xs text-gray-400">
              {category === 'TWO_PAIR'
                ? 'Higher pair rank'
                : category === 'FULL_HOUSE'
                  ? 'Three-of-a-kind rank'
                  : isStraight
                    ? 'Straight high card'
                    : 'Rank'}
            </span>
            <select
              className={inputClass}
              value={rank1}
              disabled={disabled}
              onChange={(event) => setRank1(Number(event.target.value))}
            >
              {ranks.map((rank) => (
                <option key={rank.value} value={rank.value}>
                  {rank.label}
                </option>
              ))}
            </select>
          </label>
        )}

        {needsTwoRanks && (
          <label className="space-y-2">
            <span className="text-xs text-gray-400">
              {category === 'TWO_PAIR' ? 'Lower pair rank' : 'Pair rank'}
            </span>
            <select
              className={inputClass}
              value={rank2}
              disabled={disabled}
              onChange={(event) => setRank2(Number(event.target.value))}
            >
              {ranks.map((rank) => (
                <option key={rank.value} value={rank.value}>
                  {rank.label}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      {!valid && (
        <p className="text-sm text-red-400 mt-4">
          {category === 'STRAIGHT_FLUSH' && rank1 > 13
            ? 'Ace-high Straight Flush is a Royal Flush. Select Royal Flush instead.'
            : isStraight && rank1 < 6
                ? 'The lowest permitted Straight is 6-high.'
                : 'Select two different ranks. The higher pair must come first.'}
        </p>
      )}

      <div className="mt-5 bg-[#101713] border border-emerald-500/20 rounded-xl p-4">
        <p className="text-xs text-gray-500 tracking-widest mb-2">
          BID PREVIEW
        </p>
        <p className="text-lg font-bold text-amber-300">{preview()}</p>
      </div>

      <button
        type="button"
        disabled={disabled || !valid}
        onClick={() => onSubmit(createBid())}
        className="mt-5 w-full flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-40 disabled:cursor-not-allowed text-[#0c1b13] font-bold py-3.5 rounded-xl transition-colors"
      >
        <ArrowUp size={18} />
        Raise Bid
      </button>
    </section>
  )
}

export default BidBuilder
