import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { Download, Clock, TrendingUp, DollarSign, Users, Calendar } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import DemoLabel from '@/components/shared/DemoLabel'
import { mockAnalyticsData } from '@/data/mockData'
import { cn, formatCurrency } from '@/lib/utils'

const DATE_FILTERS = ['Last 7d', 'Last 30d', 'Last 90d', 'Custom']

const funnelData = [
  { stage: 'Dormant', count: 1247 },
  { stage: 'Enrolled', count: 847 },
  { stage: 'Opened', count: 612 },
  { stage: 'Replied', count: 187 },
  { stage: 'Meeting', count: 38 },
  { stage: 'Converted', count: 12 },
]

const segmentRevenue = [
  { segment: 'Pricing', revenue: 284000 },
  { segment: 'Timing', revenue: 248000 },
  { segment: 'Ghosted', revenue: 92000 },
  { segment: 'Budget', revenue: 76000 },
  { segment: 'Competitor', revenue: 154000 },
]

const campaignComparison = [
  { name: 'Q2 Pricing', open: 68.4, reply: 22.1, meeting: 17.0 },
  { name: 'Timing Q3', open: 71.2, reply: 18.5, meeting: 17.7 },
  { name: 'Ghost Rec', open: 52.3, reply: 9.7, meeting: 9.7 },
  { name: 'Budget', open: 61.5, reply: 14.3, meeting: 17.9 },
  { name: 'Comp WB', open: 79.3, reply: 31.5, meeting: 31.6 },
]

const sdrLeaderboard = [
  { name: 'Alex Rivera', approved: 47, meetings: 18, revenue: 312000, responseTime: '1.2h', convRate: 38 },
  { name: 'Jordan Kim', approved: 39, meetings: 15, revenue: 241000, responseTime: '2.1h', convRate: 38 },
  { name: 'Sam Torres', approved: 28, meetings: 10, revenue: 201000, responseTime: '3.4h', convRate: 36 },
]

const cohortData = [
  { cohort: 'Jan 2026', enrolled: 89, w4: '8%', w8: '14%', w12: '19%' },
  { cohort: 'Feb 2026', enrolled: 112, w4: '11%', w8: '16%', w12: '21%' },
  { cohort: 'Mar 2026', enrolled: 98, w4: '9%', w8: '13%', w12: null },
  { cohort: 'Apr 2026', enrolled: 134, w4: '12%', w8: null, w12: null },
  { cohort: 'May 2026', enrolled: 67, w4: null, w8: null, w12: null },
]

const container = { hidden: {}, show: { transition: { staggerChildren: 0.07 } } }
const item = { hidden: { opacity: 0, y: 14 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }

export default function Analytics() {
  const [dateFilter, setDateFilter] = useState('Last 30d')
  const [exported, setExported] = useState<string | null>(null)

  const chartData = mockAnalyticsData.map(d => ({
    date: d.date.slice(5),
    Revenue: Math.round(d.revenue / 1000),
    Leads: d.leads,
    Meetings: d.meetings,
  }))

  function handleExport(type: string) {
    setExported(type)
    setTimeout(() => setExported(null), 2000)
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground">Analytics</h1>
          <p className="text-xs text-muted-foreground mt-0.5">Revenue recovery performance insights</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 border border-border rounded-md p-0.5">
            {DATE_FILTERS.map(f => (
              <button
                key={f}
                onClick={() => setDateFilter(f)}
                className={cn("px-2.5 py-1 rounded text-xs font-medium transition-colors",
                  dateFilter === f ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {f}
              </button>
            ))}
          </div>
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => handleExport('CSV')}>
            <Download className="h-3.5 w-3.5" />
            {exported === 'CSV' ? 'Exported!' : 'Export CSV'}
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => handleExport('PDF')}>
            <Download className="h-3.5 w-3.5" />
            {exported === 'PDF' ? 'Exported!' : 'Export PDF'}
          </Button>
        </div>
      </div>

      {/* KPI Row */}
      <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-4 gap-4">
        {[
          { label: 'Revenue Recovered', value: '$754K', icon: DollarSign, change: '+23%', color: 'text-green-400', iconBg: 'bg-green-500/10' },
          { label: 'Conversion Rate', value: '8.4%', icon: TrendingUp, change: '+1.2pp', color: 'text-blue-400', iconBg: 'bg-blue-500/10' },
          { label: 'Avg Response Time', value: '2.2h', icon: Clock, change: '-18%', color: 'text-purple-400', iconBg: 'bg-purple-500/10' },
          { label: 'ROI Multiple', value: '10.4x', icon: TrendingUp, change: '+0.8x', color: 'text-orange-400', iconBg: 'bg-orange-500/10' },
        ].map((kpi, i) => (
          <motion.div key={kpi.label} variants={item}>
            <Card>
              <CardContent className="p-4 flex items-start gap-3">
                <div className={cn("p-2 rounded-lg", kpi.iconBg)}>
                  <kpi.icon className={cn("h-4 w-4", kpi.color)} />
                </div>
                <div>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wide">{kpi.label}</p>
                  <p className="text-xl font-bold text-foreground mt-0.5">{kpi.value}</p>
                  <p className="text-[10px] text-green-400 mt-0.5">{kpi.change} vs prev period</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* Charts 2x2 */}
      <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-2 gap-4">
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
                <LineChart data={chartData} margin={{ top: 5, right: 10, bottom: 0, left: -10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 32% 17%)" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} />
                  <YAxis tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} tickFormatter={v => `$${v}K`} />
                  <Tooltip contentStyle={{ backgroundColor: 'hsl(222 47% 8%)', border: '1px solid hsl(217 32% 17%)', borderRadius: 6, fontSize: 11 }} formatter={(v) => [`$${v}K`]} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line type="monotone" dataKey="Revenue" stroke="#3b82f6" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={item}>
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">Lead Recovery Funnel</CardTitle>
                <DemoLabel />
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={200}>
                <BarChart layout="vertical" data={funnelData} margin={{ top: 0, right: 40, bottom: 0, left: 0 }}>
                  <XAxis type="number" tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} />
                  <YAxis dataKey="stage" type="category" tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} width={60} />
                  <Tooltip contentStyle={{ backgroundColor: 'hsl(222 47% 8%)', border: '1px solid hsl(217 32% 17%)', borderRadius: 6, fontSize: 11 }} />
                  <Bar dataKey="count" fill="#3b82f6" radius={[0, 3, 3, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={item}>
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">Segment Revenue Performance</CardTitle>
                <DemoLabel />
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={segmentRevenue} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 32% 17%)" />
                  <XAxis dataKey="segment" tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} />
                  <YAxis tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} tickFormatter={v => `$${Math.round(v / 1000)}K`} />
                  <Tooltip contentStyle={{ backgroundColor: 'hsl(222 47% 8%)', border: '1px solid hsl(217 32% 17%)', borderRadius: 6, fontSize: 11 }} formatter={(v) => [typeof v === 'number' ? formatCurrency(v) : v]} />
                  <Bar dataKey="revenue" fill="#22c55e" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={item}>
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">Campaign Comparison</CardTitle>
                <DemoLabel />
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={campaignComparison} margin={{ top: 5, right: 10, bottom: 15, left: -10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 32% 17%)" />
                  <XAxis dataKey="name" tick={{ fontSize: 9, fill: 'hsl(215 20% 55%)' }} angle={-15} textAnchor="end" />
                  <YAxis tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} tickFormatter={v => `${v}%`} />
                  <Tooltip contentStyle={{ backgroundColor: 'hsl(222 47% 8%)', border: '1px solid hsl(217 32% 17%)', borderRadius: 6, fontSize: 11 }} />
                  <Legend wrapperStyle={{ fontSize: 10 }} />
                  <Bar dataKey="open" name="Open %" fill="#3b82f6" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="reply" name="Reply %" fill="#22c55e" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="meeting" name="Meeting %" fill="#f97316" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* SDR Leaderboard */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm">SDR Leaderboard</CardTitle>
              <DemoLabel label="Sample Data" />
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left pb-2 text-muted-foreground font-medium">#</th>
                  <th className="text-left pb-2 text-muted-foreground font-medium">SDR</th>
                  <th className="text-left pb-2 text-muted-foreground font-medium">Approved</th>
                  <th className="text-left pb-2 text-muted-foreground font-medium">Meetings</th>
                  <th className="text-left pb-2 text-muted-foreground font-medium">Revenue</th>
                  <th className="text-left pb-2 text-muted-foreground font-medium">Avg Response</th>
                  <th className="text-left pb-2 text-muted-foreground font-medium">Conv %</th>
                </tr>
              </thead>
              <tbody>
                {sdrLeaderboard.map((sdr, i) => (
                  <tr key={sdr.name} className="border-b border-border last:border-0 hover:bg-muted/10">
                    <td className="py-2 pr-2">
                      <span className={cn("w-5 h-5 rounded-full inline-flex items-center justify-center text-[10px] font-bold",
                        i === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                        i === 1 ? 'bg-gray-500/20 text-gray-400' :
                        'bg-orange-500/20 text-orange-400'
                      )}>
                        {i + 1}
                      </span>
                    </td>
                    <td className="py-2 font-medium text-foreground">{sdr.name}</td>
                    <td className="py-2 text-muted-foreground">{sdr.approved}</td>
                    <td className="py-2 text-muted-foreground">{sdr.meetings}</td>
                    <td className="py-2 font-medium text-green-400">{formatCurrency(sdr.revenue)}</td>
                    <td className="py-2 text-muted-foreground">{sdr.responseTime}</td>
                    <td className="py-2">
                      <span className="text-foreground font-medium">{sdr.convRate}%</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </motion.div>

      {/* Cohort Analysis */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm">Lead Cohort Conversion Analysis</CardTitle>
              <DemoLabel label="Sample Cohort" />
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left pb-2 text-muted-foreground font-medium">Cohort</th>
                  <th className="text-left pb-2 text-muted-foreground font-medium">Enrolled</th>
                  <th className="text-left pb-2 text-muted-foreground font-medium">4-Week Conv</th>
                  <th className="text-left pb-2 text-muted-foreground font-medium">8-Week Conv</th>
                  <th className="text-left pb-2 text-muted-foreground font-medium">12-Week Conv</th>
                </tr>
              </thead>
              <tbody>
                {cohortData.map(row => (
                  <tr key={row.cohort} className="border-b border-border last:border-0 hover:bg-muted/10">
                    <td className="py-2 font-medium text-foreground">{row.cohort}</td>
                    <td className="py-2 text-muted-foreground">{row.enrolled}</td>
                    {[row.w4, row.w8, row.w12].map((v, i) => (
                      <td key={i} className="py-2">
                        {v ? (
                          <span className={cn("px-1.5 py-0.5 rounded text-[10px] font-medium",
                            parseFloat(v) >= 18 ? 'bg-green-500/20 text-green-400' :
                            parseFloat(v) >= 12 ? 'bg-blue-500/20 text-blue-400' :
                            'bg-muted text-muted-foreground'
                          )}>
                            {v}
                          </span>
                        ) : (
                          <span className="text-muted-foreground/40 text-[10px]">—</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
