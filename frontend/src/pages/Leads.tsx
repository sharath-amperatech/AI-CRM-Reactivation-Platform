import { useState, useMemo, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, ChevronUp, ChevronDown, ChevronLeft, ChevronRight,
  Filter, Download, Zap, RefreshCw, CheckSquare, Square
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import SegmentBadge from '@/components/shared/SegmentBadge'
import ConfidenceBar from '@/components/shared/ConfidenceBar'
import { statusColors, LeadSegment, LeadStatus, type Lead } from '@/data/mockData'
import { cn, formatCurrency, getRelativeTime } from '@/lib/utils'
import { fetchLeads } from '@/lib/api'

type SortKey = 'name' | 'segment' | 'status' | 'confidence' | 'dealValue' | 'inactiveDays' | 'lastActivity' | 'assignedTo'
type SortDir = 'asc' | 'desc'

const SEGMENTS: (LeadSegment | 'all')[] = ['all', 'pricing_objection', 'timing_issue', 'competitor_loss', 'ghosted', 'no_decision_maker', 'budget_constraints', 'feature_gap']
const STATUSES: (LeadStatus | 'all')[] = ['all', 'dormant', 'active', 'reactivated', 'meeting_booked', 'lost']
const SEGMENT_LABELS: Record<string, string> = {
  all: 'All Segments',
  pricing_objection: 'Pricing Objection',
  timing_issue: 'Timing Issue',
  competitor_loss: 'Competitor Loss',
  ghosted: 'Ghosted',
  no_decision_maker: 'No Decision Maker',
  budget_constraints: 'Budget Constraints',
  feature_gap: 'Feature Gap',
}
const STATUS_LABELS: Record<string, string> = {
  all: 'All Statuses',
  dormant: 'Dormant',
  active: 'Active',
  reactivated: 'Reactivated',
  meeting_booked: 'Meeting Booked',
  lost: 'Lost',
}

const PAGE_SIZE = 8

export default function Leads() {
  const navigate = useNavigate()
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [segment, setSegment] = useState<LeadSegment | 'all'>('all')
  const [status, setStatus] = useState<LeadStatus | 'all'>('all')
  const [sortKey, setSortKey] = useState<SortKey>('confidence')
  const [sortDir, setSortDir] = useState<SortDir>('desc')
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [page, setPage] = useState(1)

  useEffect(() => {
    fetchLeads()
      .then(({ leads }) => setLeads(leads))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    let list = [...leads]
    if (search) {
      const q = search.toLowerCase()
      list = list.filter(l => l.name.toLowerCase().includes(q) || l.company.toLowerCase().includes(q) || l.email.toLowerCase().includes(q))
    }
    if (segment !== 'all') list = list.filter(l => l.segment === segment)
    if (status !== 'all') list = list.filter(l => l.status === status)
    list.sort((a, b) => {
      const av = a[sortKey]
      const bv = b[sortKey]
      const cmp = av < bv ? -1 : av > bv ? 1 : 0
      return sortDir === 'asc' ? cmp : -cmp
    })
    return list
  }, [leads, search, segment, status, sortKey, sortDir])

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)
  const paged = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  function handleSort(key: SortKey) {
    if (key === sortKey) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('desc') }
  }

  function toggleSelect(id: string) {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  function toggleAll() {
    if (selected.size === paged.length) setSelected(new Set())
    else setSelected(new Set(paged.map(l => l.id)))
  }

  function SortIcon({ k }: { k: SortKey }) {
    if (sortKey !== k) return <ChevronUp className="h-3 w-3 opacity-20" />
    return sortDir === 'asc' ? <ChevronUp className="h-3 w-3 text-primary" /> : <ChevronDown className="h-3 w-3 text-primary" />
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground">Dormant Leads</h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            {filtered.length} leads · {leads.length} total
          </p>
        </div>
        <Button size="sm" className="gap-1.5">
          <Zap className="h-3.5 w-3.5" /> Enroll in Campaign
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
        <div className="relative flex-1 min-w-[200px] max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
          <Input
            placeholder="Search leads..."
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1) }}
            className="pl-8 h-8 text-xs"
          />
        </div>
        <select
          value={segment}
          onChange={e => { setSegment(e.target.value as LeadSegment | 'all'); setPage(1) }}
          className="h-8 rounded-md border border-border bg-card text-xs text-foreground px-2 focus:outline-none focus:ring-1 focus:ring-ring"
        >
          {SEGMENTS.map(s => <option key={s} value={s}>{SEGMENT_LABELS[s]}</option>)}
        </select>
        <select
          value={status}
          onChange={e => { setStatus(e.target.value as LeadStatus | 'all'); setPage(1) }}
          className="h-8 rounded-md border border-border bg-card text-xs text-foreground px-2 focus:outline-none focus:ring-1 focus:ring-ring"
        >
          {STATUSES.map(s => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
        </select>
        <Button variant="outline" size="sm" className="gap-1.5">
          <Filter className="h-3.5 w-3.5" /> More Filters
        </Button>
      </div>

      {/* Bulk Action Bar */}
      <AnimatePresence>
        {selected.size > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-lg px-4 py-2"
          >
            <span className="text-xs font-medium text-primary">{selected.size} selected</span>
            <div className="flex items-center gap-2 ml-2">
              <Button size="sm" className="h-7 text-xs gap-1">
                <Zap className="h-3 w-3" /> Enroll in Campaign
              </Button>
              <Button size="sm" variant="outline" className="h-7 text-xs gap-1">
                <Download className="h-3 w-3" /> Export
              </Button>
              <Button size="sm" variant="outline" className="h-7 text-xs gap-1">
                <RefreshCw className="h-3 w-3" /> Reclassify
              </Button>
            </div>
            <Button size="sm" variant="ghost" className="h-7 text-xs ml-auto" onClick={() => setSelected(new Set())}>
              Clear
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="w-8 px-3 py-2.5">
                  <button onClick={toggleAll}>
                    {selected.size === paged.length && paged.length > 0
                      ? <CheckSquare className="h-3.5 w-3.5 text-primary" />
                      : <Square className="h-3.5 w-3.5 text-muted-foreground" />}
                  </button>
                </th>
                {([
                  ['name', 'Lead'],
                  ['segment', 'Segment'],
                  ['status', 'Status'],
                  ['confidence', 'Confidence'],
                  ['dealValue', 'Deal Value'],
                  ['inactiveDays', 'Inactive'],
                  ['lastActivity', 'Last Activity'],
                  ['assignedTo', 'Assigned To'],
                ] as [SortKey, string][]).map(([k, label]) => (
                  <th
                    key={k}
                    className="text-left px-3 py-2.5 text-muted-foreground font-medium cursor-pointer hover:text-foreground select-none whitespace-nowrap"
                    onClick={() => handleSort(k)}
                  >
                    <span className="flex items-center gap-1">{label}<SortIcon k={k} /></span>
                  </th>
                ))}
                <th className="px-3 py-2.5 text-muted-foreground font-medium text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={10} className="text-center py-12 text-muted-foreground">
                    Loading leads...
                  </td>
                </tr>
              )}
              {!loading && paged.length === 0 && (
                <tr>
                  <td colSpan={10} className="text-center py-12 text-muted-foreground">
                    No leads match your filters.
                  </td>
                </tr>
              )}
              {paged.map(lead => (
                <motion.tr
                  key={lead.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className={cn(
                    "border-b border-border hover:bg-muted/20 cursor-pointer transition-colors",
                    selected.has(lead.id) && "bg-primary/5"
                  )}
                  onClick={() => navigate(`/leads/${lead.id}`)}
                >
                  <td className="px-3 py-2.5" onClick={e => { e.stopPropagation(); toggleSelect(lead.id) }}>
                    {selected.has(lead.id)
                      ? <CheckSquare className="h-3.5 w-3.5 text-primary" />
                      : <Square className="h-3.5 w-3.5 text-muted-foreground" />}
                  </td>
                  <td className="px-3 py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-[10px] font-bold text-primary shrink-0">
                        {lead.name[0]}
                      </div>
                      <div>
                        <p className="font-medium text-foreground whitespace-nowrap">{lead.name}</p>
                        <p className="text-muted-foreground text-[10px]">{lead.company}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-2.5"><SegmentBadge segment={lead.segment} /></td>
                  <td className="px-3 py-2.5">
                    <span className={cn("inline-flex items-center px-2 py-0.5 rounded-md border font-medium text-[10px]", statusColors[lead.status])}>
                      {lead.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 w-28">
                    <ConfidenceBar value={lead.confidence} />
                  </td>
                  <td className="px-3 py-2.5 font-medium text-foreground whitespace-nowrap">
                    {formatCurrency(lead.dealValue)}
                  </td>
                  <td className="px-3 py-2.5 text-muted-foreground whitespace-nowrap">
                    {lead.inactiveDays === 0 ? 'Active' : `${lead.inactiveDays}d`}
                  </td>
                  <td className="px-3 py-2.5 text-muted-foreground whitespace-nowrap">
                    {getRelativeTime(lead.lastActivity)}
                  </td>
                  <td className="px-3 py-2.5 text-muted-foreground whitespace-nowrap">{lead.assignedTo}</td>
                  <td className="px-3 py-2.5" onClick={e => e.stopPropagation()}>
                    <div className="flex items-center gap-1">
                      <Button size="sm" variant="ghost" className="h-6 px-2 text-[10px]" onClick={() => navigate(`/leads/${lead.id}`)}>
                        View
                      </Button>
                      <Button size="sm" variant="ghost" className="h-6 px-2 text-[10px] text-primary">
                        <Zap className="h-3 w-3" />
                      </Button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-border">
          <p className="text-xs text-muted-foreground">
            Showing {Math.min((page - 1) * PAGE_SIZE + 1, filtered.length)}–{Math.min(page * PAGE_SIZE, filtered.length)} of {filtered.length}
          </p>
          <div className="flex items-center gap-1">
            <Button size="icon-sm" variant="outline" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
              <ChevronLeft className="h-3.5 w-3.5" />
            </Button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
              <Button
                key={p}
                size="icon-sm"
                variant={p === page ? 'default' : 'outline'}
                onClick={() => setPage(p)}
                className="h-7 w-7 text-xs"
              >
                {p}
              </Button>
            ))}
            <Button size="icon-sm" variant="outline" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
              <ChevronRight className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
