import { TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { cn, formatCurrency, formatNumber, formatPercent } from '@/lib/utils'

interface KPICardProps {
  title: string
  value: string | number
  change?: number
  changeLabel?: string
  icon: React.ReactNode
  iconColor?: string
  format?: 'currency' | 'number' | 'percent' | 'raw'
  subtitle?: string
  demo?: boolean
}

export default function KPICard({
  title,
  value,
  change,
  changeLabel,
  icon,
  iconColor,
  format = 'raw',
  subtitle,
  demo = true,
}: KPICardProps) {
  const formattedValue =
    typeof value === 'number'
      ? format === 'currency'
        ? formatCurrency(value)
        : format === 'number'
        ? formatNumber(value)
        : format === 'percent'
        ? formatPercent(value)
        : String(value)
      : value

  const isPositive = (change ?? 0) >= 0

  return (
    <Card className="relative overflow-hidden">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide truncate">
              {title}
            </p>
            <p className="text-2xl font-bold mt-1 text-foreground">{formattedValue}</p>
            {change !== undefined && (
              <div
                className={cn(
                  'flex items-center gap-1 mt-1 text-xs',
                  isPositive ? 'text-green-400' : 'text-red-400'
                )}
              >
                {isPositive ? (
                  <TrendingUp className="h-3 w-3" />
                ) : (
                  <TrendingDown className="h-3 w-3" />
                )}
                <span>
                  {isPositive ? '+' : ''}
                  {formatPercent(change)} {changeLabel}
                </span>
              </div>
            )}
            {subtitle && (
              <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
            )}
          </div>
          <div className={cn('p-2 rounded-lg', iconColor || 'bg-primary/10')}>
            {icon}
          </div>
        </div>
        {demo && (
          <div className="absolute top-2 right-2">
            <span className="text-[9px] text-muted-foreground/50 font-medium">SAMPLE</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
