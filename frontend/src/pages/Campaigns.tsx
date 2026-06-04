import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutGrid, Table, Plus, FlaskConical, TrendingUp,
  Mail, ChevronDown, ChevronUp, DollarSign, Calendar, Loader2
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import SegmentBadge from '@/components/shared/SegmentBadge'
import { type Campaign, type CampaignStatus, fetchCampaigns } from '@/lib/api'
import { cn, formatCurrency } from '@/lib/utils'

const STATUS_FILTERS: (CampaignStatus | 'all')[] = ['all', 'active', 'paused', 'completed', 'draft']

const statusColors: Record<CampaignStatus, string> = {
  active: 'bg-green-500/20 text-green-400 border-green-500/30',
  paused: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  completed: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  draft: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

type SortKey = 'name' | 'enrolledLeads' | 'openRate' | 'replyRate' | 'meetingsBooked' | 'revenueRecovered'

export default function Campaigns() {
  const navigate = useNavigate()
  const [view, setView] = useState<'cards' | 'table'>('cards')
  const [statusFilter, setStatusFilter] = useState<CampaignStatus | 'all'>('all')
  const [sortKey, setSortKey] = useState<SortKey>('revenueRecovered')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    fetchCampaigns()
      .then(({ campaigns: data }) => {
        setCampaigns(data)
        setError(null)
      })
      .catch(e => setError(e instanceof Error ? e.message : 'Failed to load campaigns'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = campaigns
    .filter(c => statusFilter === 'all' || c.status === statusFilter)
    .sort((a, b) => {
      const av = a[sortKey]
      const bv = b[sortKey]
      const cmp = av < bv ? -1 : av > bv ? 1 : 0
      return sortDir === 'asc' ? cmp : -cmp
    })

  const totalRevenue = campaigns.reduce((s, c) => s + c.revenueRecovered, 0)
  const totalMeetings = campaigns.reduce((s, c) => s + c.meetingsBooked, 0)
  const active = campaigns.filter(c => c.status === 'active').length

  function handleSort(k: SortKey) {
    if (k === sortKey) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(k); setSortDir('desc') }
  }

  function SortIcon({ k }: { k: SortKey }) {
    if (sortKey !== k) return null
    return sortDir === 'asc' ? <ChevronUp className="h-3 w-3 text-primary inline" /> : <ChevronDown className="h-3 w-3 text-primary inline" />
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground">Campaigns</h1>
          <p className="text-xs text-muted-foreground mt-0.5">Manage reactivation campaigns</p>
        </div>
        <Button size="sm" className="gap-1.5" onClick={() => navigate('/campaigns/new')}>
          <Plus className="h-3.5 w-3.5" /> New Campaign
        </Button>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Total Campaigns', value: loading ? '—' : campaigns.length, icon: LayoutGrid, color: 'text-primary' },
          { label: 'Active', value: loading ? '—' : active, icon: TrendingUp, color: 'text-green-400' },
          { label: 'Revenue Recovered', value: loading ? '—' : formatCurrency(totalRevenue), icon: DollarSign, color: 'text-yellow-400' },
          { label: 'Meetings Booked', value: loading ? '—' : totalMeetings, icon: Calendar, color: 'text-purple-400' },
        ].map(stat => (
          <Card key={stat.label}>
            <CardContent className="p-4 flex items-center gap-3">
              <stat.icon className={cn("h-5 w-5", stat.color)} />
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wide">{stat.label}</p>
                <p className="text-lg font-bold text-foreground">{stat.value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters + View Toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1">
          {STATUS_FILTERS.map(s => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={cn(
                "px-3 py-1.5 rounded-md text-xs font-medium transition-colors capitalize",
                statusFilter === s ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-muted'
              )}
            >
              {s === 'all' ? 'All' : s}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-1 border border-border rounded-md p-0.5">
          <button
            onClick={() => setView('cards')}
            className={cn("p-1.5 rounded transition-colors", view === 'cards' ? 'bg-accent text-foreground' : 'text-muted-foreground hover:text-foreground')}
          >
            <LayoutGrid className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => setView('table')}
            className={cn("p-1.5 rounded transition-colors", view === 'table' ? 'bg-accent text-foreground' : 'text-muted-foreground hover:text-foreground')}
          >
            <Table className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20 text-muted-foreground gap-2">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span className="text-sm">Loading campaigns…</span>
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="rounded-md border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center gap-3">
          <p className="text-sm text-muted-foreground">No campaigns yet.</p>
          <Button size="sm" onClick={() => navigate('/campaigns/new')}>
            <Plus className="h-3.5 w-3.5 mr-1.5" /> Create your first campaign
          </Button>
        </div>
      )}

      {/* Card View */}
      {!loading && !error && view === 'cards' && filtered.length > 0 && (
        <motion.div
          layout
          className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4"
        >
          {filtered.map((campaign, i) => (
            <motion.div
              key={campaign.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => navigate(`/campaigns/${campaign.id}`)}
              className="cursor-pointer"
            >
              <Card className="hover:border-primary/40 transition-colors">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={cn("inline-flex items-center px-1.5 py-0.5 rounded border text-[10px] font-medium", statusColors[campaign.status])}>
                          {campaign.status}
                        </span>
                        {campaign.abTest && (
                          <span className="inline-flex items-center gap-1 text-[10px] text-purple-400 bg-purple-500/10 border border-purple-500/20 px-1.5 py-0.5 rounded">
                            <FlaskConical className="h-2.5 w-2.5" /> A/B
                          </span>
                        )}
                      </div>
                      <CardTitle className="text-sm leading-snug">{campaign.name}</CardTitle>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    {campaign.segment && <SegmentBadge segment={campaign.segment as never} className="text-[10px]" />}
                    <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                      <Mail className="h-3 w-3" /> {campaign.channel}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="pt-0 space-y-3">
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { label: 'Enrolled', value: campaign.enrolledLeads },
                      { label: 'Meetings', value: campaign.meetingsBooked },
                      { label: 'Converted', value: campaign.convertedLeads },
                    ].map(m => (
                      <div key={m.label} className="text-center">
                        <p className="text-sm font-bold text-foreground">{m.value}</p>
                        <p className="text-[10px] text-muted-foreground">{m.label}</p>
                      </div>
                    ))}
                  </div>
                  <div className="space-y-1.5">
                    {[
                      { label: 'Open Rate', value: campaign.openRate, color: 'bg-blue-500' },
                      { label: 'Reply Rate', value: campaign.replyRate, color: 'bg-green-500' },
                    ].map(m => (
                      <div key={m.label}>
                        <div className="flex justify-between text-[10px] mb-0.5">
                          <span className="text-muted-foreground">{m.label}</span>
                          <span className="text-foreground font-medium">{m.value}%</span>
                        </div>
                        <div className="h-1 bg-muted rounded-full">
                          <div className={cn("h-1 rounded-full", m.color)} style={{ width: `${Math.min(m.value, 100)}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="flex items-center justify-between pt-1 border-t border-border">
                    <span className="text-[10px] text-muted-foreground">Step {campaign.stepsCompleted}/{campaign.totalSteps}</span>
                    <span className="text-xs font-bold text-green-400">{formatCurrency(campaign.revenueRecovered)}</span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Table View */}
      {!loading && !error && view === 'table' && filtered.length > 0 && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  {([
                    ['name', 'Campaign'],
                    ['enrolledLeads', 'Enrolled'],
                    ['openRate', 'Open %'],
                    ['replyRate', 'Reply %'],
                    ['meetingsBooked', 'Meetings'],
                    ['revenueRecovered', 'Revenue'],
                  ] as [SortKey, string][]).map(([k, label]) => (
                    <th
                      key={k}
                      className="text-left px-4 py-2.5 text-muted-foreground font-medium cursor-pointer hover:text-foreground whitespace-nowrap"
                      onClick={() => handleSort(k)}
                    >
                      {label} <SortIcon k={k} />
                    </th>
                  ))}
                  <th className="text-left px-4 py-2.5 text-muted-foreground font-medium">Segment</th>
                  <th className="text-left px-4 py-2.5 text-muted-foreground font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(c => (
                  <tr
                    key={c.id}
                    className="border-b border-border hover:bg-muted/20 cursor-pointer transition-colors"
                    onClick={() => navigate(`/campaigns/${c.id}`)}
                  >
                    <td className="px-4 py-2.5">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-foreground">{c.name}</span>
                        {c.abTest && <span className="text-[10px] text-purple-400 bg-purple-500/10 px-1 rounded">A/B</span>}
                      </div>
                    </td>
                    <td className="px-4 py-2.5 text-muted-foreground">{c.enrolledLeads}</td>
                    <td className="px-4 py-2.5 text-foreground">{c.openRate}%</td>
                    <td className="px-4 py-2.5 text-foreground">{c.replyRate}%</td>
                    <td className="px-4 py-2.5 text-foreground">{c.meetingsBooked}</td>
                    <td className="px-4 py-2.5 font-medium text-green-400">{formatCurrency(c.revenueRecovered)}</td>
                    <td className="px-4 py-2.5">
                      {c.segment && <SegmentBadge segment={c.segment as never} />}
                    </td>
                    <td className="px-4 py-2.5">
                      <span className={cn("inline-flex items-center px-1.5 py-0.5 rounded border text-[10px] font-medium", statusColors[c.status])}>
                        {c.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
