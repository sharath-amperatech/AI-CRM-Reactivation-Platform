import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import {
  DollarSign, Users, Calendar, Zap, MessageSquare,
  Activity, CheckCircle, Clock, RefreshCw, Filter, ChevronDown
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import KPICard from '@/components/shared/KPICard'
import DemoLabel from '@/components/shared/DemoLabel'
import { mockAnalyticsData } from '@/data/mockData'
import { cn } from '@/lib/utils'

const DATE_FILTERS = ['Last 7 days', 'Last 30 days', 'Last 90 days', 'Custom']

const aiActivity = [
  { icon: Activity, text: 'Classified 23 leads — Pricing Objection detected', time: '2m ago', color: 'text-blue-400' },
  { icon: MessageSquare, text: 'Generated 8 outreach emails for Campaign 001', time: '15m ago', color: 'text-green-400' },
  { icon: RefreshCw, text: 'Retrieved CRM context for Sarah Chen (4 chunks)', time: '28m ago', color: 'text-purple-400' },
  { icon: CheckCircle, text: 'RAG evaluation completed — Faithfulness: 0.91', time: '1h ago', color: 'text-yellow-400' },
  { icon: RefreshCw, text: 'HubSpot sync completed — 147 new activities ingested', time: '2h ago', color: 'text-orange-400' },
]

const recentApprovals = [
  { name: 'Sarah Chen', company: 'TechFlow Solutions', confidence: 91, status: 'pending' },
  { name: 'Marcus Williams', company: 'GrowthBase Inc', confidence: 84, status: 'pending' },
  { name: 'Elena Rodriguez', company: 'CloudFirst Systems', confidence: 88, status: 'pending' },
  { name: 'Natasha Ivanova', company: 'DataSphere Analytics', confidence: 86, status: 'approved' },
]

const funnelData = [
  { stage: 'Dormant', count: 1247 },
  { stage: 'Enrolled', count: 847 },
  { stage: 'Opened', count: 612 },
  { stage: 'Replied', count: 187 },
  { stage: 'Meeting', count: 38 },
  { stage: 'Converted', count: 12 },
]

const segmentData = [
  { name: 'Pricing', value: 32, color: '#f97316' },
  { name: 'Timing', value: 28, color: '#3b82f6' },
  { name: 'Ghosted', value: 18, color: '#6b7280' },
  { name: 'Budget', value: 14, color: '#eab308' },
  { name: 'Other', value: 8, color: '#8b5cf6' },
]

const campaignPerf = [
  { name: 'Q2 Pricing', openRate: 68.4, replyRate: 22.1, meetings: 8 },
  { name: 'Timing Q3', openRate: 71.2, replyRate: 18.5, meetings: 11 },
  { name: 'Ghost Recovery', openRate: 52.3, replyRate: 9.7, meetings: 3 },
  { name: 'Budget Unlock', openRate: 61.5, replyRate: 14.3, meetings: 5 },
  { name: 'Competitor WB', openRate: 79.3, replyRate: 31.5, meetings: 6 },
]

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
}
const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35 } },
}

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [dateFilter, setDateFilter] = useState('Last 30 days')
  const [dateOpen, setDateOpen] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setLoading(false), 1400)
    return () => clearTimeout(t)
  }, [])

  const chartData = mockAnalyticsData.map(d => ({
    date: d.date.slice(5),
    Revenue: Math.round(d.revenue / 1000),
    Leads: d.leads,
    Meetings: d.meetings,
  }))

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground">Command Center</h1>
          <p className="text-xs text-muted-foreground mt-0.5">AI-powered reactivation pipeline overview</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Button variant="outline" size="sm" onClick={() => setDateOpen(!dateOpen)} className="gap-1.5">
              <Clock className="h-3.5 w-3.5" />
              {dateFilter}
              <ChevronDown className="h-3.5 w-3.5" />
            </Button>
            {dateOpen && (
              <div className="absolute right-0 top-full mt-1 w-40 bg-card border border-border rounded-lg shadow-xl z-10">
                {DATE_FILTERS.map(f => (
                  <button
                    key={f}
                    className={cn("w-full text-left px-3 py-1.5 text-xs transition-colors hover:bg-accent", dateFilter === f ? 'text-primary' : 'text-muted-foreground')}
                    onClick={() => { setDateFilter(f); setDateOpen(false) }}
                  >
                    {f}
                  </button>
                ))}
              </div>
            )}
          </div>
          <Button variant="outline" size="sm" className="gap-1.5">
            <Filter className="h-3.5 w-3.5" />
            Filter
          </Button>
        </div>
      </div>

      {/* KPI Row */}
      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <Card key={i}><CardContent className="p-4"><Skeleton className="h-16 w-full" /></CardContent></Card>
          ))}
        </div>
      ) : (
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4"
        >
          <motion.div variants={item}>
            <KPICard
              title="Revenue Recovered"
              value={754000}
              format="currency"
              change={23.4}
              changeLabel="vs last period"
              icon={<DollarSign className="h-4 w-4 text-green-400" />}
              iconColor="bg-green-500/10"
            />
          </motion.div>
          <motion.div variants={item}>
            <KPICard
              title="Active Leads"
              value={247}
              format="number"
              change={12.1}
              changeLabel="vs last period"
              icon={<Users className="h-4 w-4 text-blue-400" />}
              iconColor="bg-blue-500/10"
            />
          </motion.div>
          <motion.div variants={item}>
            <KPICard
              title="Meetings Booked"
              value={38}
              format="number"
              change={31.0}
              changeLabel="vs last period"
              icon={<Calendar className="h-4 w-4 text-purple-400" />}
              iconColor="bg-purple-500/10"
            />
          </motion.div>
          <motion.div variants={item}>
            <KPICard
              title="Campaigns Running"
              value={4}
              format="raw"
              icon={<Zap className="h-4 w-4 text-orange-400" />}
              iconColor="bg-orange-500/10"
              subtitle="3 active · 1 paused"
            />
          </motion.div>
          <motion.div variants={item}>
            <KPICard
              title="AI Messages Generated"
              value={1847}
              format="number"
              change={8.7}
              changeLabel="this period"
              icon={<MessageSquare className="h-4 w-4 text-primary" />}
              iconColor="bg-primary/10"
            />
          </motion.div>
        </motion.div>
      )}

      {/* Main content grid */}
      {loading ? (
        <div className="grid grid-cols-5 gap-4">
          <div className="col-span-3 space-y-4">
            <Skeleton className="h-56 w-full rounded-lg" />
            <Skeleton className="h-48 w-full rounded-lg" />
          </div>
          <div className="col-span-2 space-y-4">
            <Skeleton className="h-48 w-full rounded-lg" />
            <Skeleton className="h-56 w-full rounded-lg" />
          </div>
        </div>
      ) : (
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-5 gap-4"
        >
          {/* Left column */}
          <div className="col-span-3 space-y-4">
            {/* Revenue Line Chart */}
            <motion.div variants={item}>
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">Revenue Recovery Trend</CardTitle>
                    <DemoLabel />
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 32% 17%)" />
                      <XAxis dataKey="date" tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} />
                      <YAxis tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} tickFormatter={v => `$${v}K`} />
                      <Tooltip
                        contentStyle={{ backgroundColor: 'hsl(222 47% 8%)', border: '1px solid hsl(217 32% 17%)', borderRadius: 6, fontSize: 12 }}
                        formatter={(v) => [`$${v}K`, 'Revenue']}
                      />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      <Line type="monotone" dataKey="Revenue" stroke="#3b82f6" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="Meetings" stroke="#22c55e" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>

            {/* Campaign Performance Bar Chart */}
            <motion.div variants={item}>
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">Campaign Performance</CardTitle>
                    <DemoLabel />
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={campaignPerf} margin={{ top: 5, right: 5, bottom: 20, left: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 32% 17%)" />
                      <XAxis dataKey="name" tick={{ fontSize: 9, fill: 'hsl(215 20% 55%)' }} angle={-20} textAnchor="end" />
                      <YAxis tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} tickFormatter={v => `${v}%`} />
                      <Tooltip contentStyle={{ backgroundColor: 'hsl(222 47% 8%)', border: '1px solid hsl(217 32% 17%)', borderRadius: 6, fontSize: 12 }} />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      <Bar dataKey="openRate" name="Open %" fill="#3b82f6" radius={[2, 2, 0, 0]} />
                      <Bar dataKey="replyRate" name="Reply %" fill="#22c55e" radius={[2, 2, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Right column */}
          <div className="col-span-2 space-y-4">
            {/* AI Activity Feed */}
            <motion.div variants={item}>
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                      AI Activity Feed
                    </CardTitle>
                    <DemoLabel label="Simulated" />
                  </div>
                </CardHeader>
                <CardContent className="pt-0 space-y-0">
                  {aiActivity.map((act, i) => (
                    <div key={i} className="flex items-start gap-2.5 py-2 border-b border-border last:border-0">
                      <act.icon className={cn("h-3.5 w-3.5 mt-0.5 shrink-0", act.color)} />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-foreground leading-relaxed">{act.text}</p>
                        <p className="text-[10px] text-muted-foreground mt-0.5">{act.time}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>

            {/* Recent Approvals */}
            <motion.div variants={item}>
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">Recent Approvals</CardTitle>
                    <span className="text-[10px] text-primary font-medium cursor-pointer hover:underline">View all →</span>
                  </div>
                </CardHeader>
                <CardContent className="pt-0 space-y-0">
                  {recentApprovals.map((a, i) => (
                    <div key={i} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                      <div className="flex items-center gap-2 min-w-0">
                        <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-[10px] font-bold text-primary shrink-0">
                          {a.name[0]}
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-medium text-foreground truncate">{a.name}</p>
                          <p className="text-[10px] text-muted-foreground truncate">{a.company}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <span className="text-xs font-semibold text-green-400">{a.confidence}%</span>
                        <span className={cn("text-[10px] px-1.5 py-0.5 rounded border font-medium",
                          a.status === 'pending'
                            ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'
                            : 'bg-green-500/10 text-green-400 border-green-500/30'
                        )}>
                          {a.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </motion.div>
      )}

      {/* Bottom row */}
      {!loading && (
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-3 gap-4"
        >
          {/* Lead Recovery Funnel */}
          <motion.div variants={item}>
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">Lead Recovery Funnel</CardTitle>
                  <DemoLabel />
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart layout="vertical" data={funnelData} margin={{ top: 0, right: 40, bottom: 0, left: 0 }}>
                    <XAxis type="number" tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} />
                    <YAxis dataKey="stage" type="category" tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} width={60} />
                    <Tooltip contentStyle={{ backgroundColor: 'hsl(222 47% 8%)', border: '1px solid hsl(217 32% 17%)', borderRadius: 6, fontSize: 12 }} />
                    <Bar dataKey="count" fill="#3b82f6" radius={[0, 3, 3, 0]}>
                      {funnelData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={`hsl(217 91% ${60 - index * 8}%)`} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>

          {/* Segment Pie Chart */}
          <motion.div variants={item}>
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">Segment Breakdown</CardTitle>
                  <DemoLabel />
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex items-center gap-2">
                  <ResponsiveContainer width="60%" height={160}>
                    <PieChart>
                      <Pie data={segmentData} cx="50%" cy="50%" innerRadius={40} outerRadius={65} dataKey="value">
                        {segmentData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: 'hsl(222 47% 8%)', border: '1px solid hsl(217 32% 17%)', borderRadius: 6, fontSize: 12 }} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="space-y-1.5 flex-1">
                    {segmentData.map(s => (
                      <div key={s.name} className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: s.color }} />
                        <span className="text-[10px] text-muted-foreground">{s.name}</span>
                        <span className="text-[10px] font-semibold text-foreground ml-auto">{s.value}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* AI Cost Metrics */}
          <motion.div variants={item}>
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">AI Cost Metrics</CardTitle>
                  <DemoLabel label="Sample" />
                </div>
              </CardHeader>
              <CardContent className="pt-0 space-y-3">
                {[
                  { label: 'Total API Cost (MTD)', value: '$284.12', sub: 'GPT-4o + Cohere + Embeddings' },
                  { label: 'Cost per Message', value: '$0.15', sub: 'avg across all campaigns' },
                  { label: 'Cache Hit Rate', value: '62%', sub: 'semantic cache savings: $81' },
                  { label: 'Avg Latency', value: '1.8s', sub: 'p50 end-to-end pipeline' },
                  { label: 'RAG Retrievals', value: '4,218', sub: 'total chunks fetched this month' },
                ].map(m => (
                  <div key={m.label} className="flex items-center justify-between">
                    <div>
                      <p className="text-xs text-muted-foreground">{m.label}</p>
                      <p className="text-[10px] text-muted-foreground/60">{m.sub}</p>
                    </div>
                    <span className="text-sm font-bold text-foreground">{m.value}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}
