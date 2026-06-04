import { cn } from '@/lib/utils'

export default function ConfidenceBar({
  value,
  showLabel = true,
}: {
  value: number
  showLabel?: boolean
}) {
  const pct = Math.round(value * 100)
  const color =
    pct >= 80 ? 'bg-green-500' : pct >= 60 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-muted rounded-full h-1.5">
        <div
          className={cn('h-1.5 rounded-full transition-all', color)}
          style={{ width: `${pct}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-xs text-muted-foreground w-8 text-right">{pct}%</span>
      )}
    </div>
  )
}
