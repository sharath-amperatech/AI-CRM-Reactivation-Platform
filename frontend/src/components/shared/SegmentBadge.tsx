import { segmentLabels, segmentColors } from '@/data/mockData'
import { cn } from '@/lib/utils'

export default function SegmentBadge({
  segment,
  className,
}: {
  segment: string
  className?: string
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border',
        segmentColors[segment] || 'bg-gray-500/20 text-gray-400 border-gray-500/30',
        className
      )}
    >
      {segmentLabels[segment] || segment}
    </span>
  )
}
