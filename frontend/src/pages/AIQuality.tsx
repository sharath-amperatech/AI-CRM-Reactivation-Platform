import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer
} from 'recharts'
import {
  Brain, CheckCircle, XCircle, AlertTriangle, RefreshCw,
  Eye, TrendingUp, Database, Zap, Clock
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import DemoLabel from '@/components/shared/DemoLabel'
import { mockRAGASMetrics } from '@/data/mockData'
import { cn } from '@/lib/utils'

const ragas = [
  { key: 'faithfulness', label: 'Faithfulness', value: 0.93, target: 0.85, color: '#3b82f6', trend: '+0.08' },
  { key: 'answerRelevancy', label: 'Answer Relevancy', value: 0.91, target: 0.85, color: '#22c55e', trend: '+0.12' },
  { key: 'contextRecall', label: 'Context Recall', value: 0.87, target: 0.80, color: '#f97316', trend: '+0.16' },
  { key: 'contextPrecision', label: 'Context Precision', value: 0.90, target: 0.85, color: '#a855f7', trend: '+0.14' },
]

const chartData = mockRAGASMetrics.map(d => ({
  date: d.date.slice(5),
  Faithfulness: d.faithfulness,
  'Answer Rel.': d.answerRelevancy,
  'Ctx Recall': d.contextRecall,
  'Ctx Precision': d.contextPrecision,
}))

const failingGenerations = [
  { id: 'gen-012', lead: 'Tyler Brennan', segment: 'no_decision_maker', faithfulness: 0.61, issue: 'Hallucinated deal size not in CRM', status: 'flagged' },
  { id: 'gen-019', lead: 'Carlos Mendez', segment: 'ghosted', faithfulness: 0.68, issue: 'Context window exceeded — partial retrieval', status: 'flagged' },
  { id: 'gen-027', lead: 'Unknown Lead', segment: 'unknown', faithfulness: 0.55, issue: 'Low-quality embedding match (similarity < 0.5)', status: 'dropped' },
]

const recentEvals = [
  { id: 'eval-008', time: '2026-05-25 07:00', samples: 47, pass: 44, fail: 3, avgFaithfulness: 0.91, status: 'pass' },
  { id: 'eval-007', time: '2026-05-24 07:00', samples: 52, pass: 48, fail: 4, avgFaithfulness: 0.89, status: 'pass' },
  { id: 'eval-006', time: '2026-05-23 07:00', samples: 41, pass: 36, fail: 5, avgFaithfulness: 0.87, status: 'pass' },
  { id: 'eval-005', time: '2026-05-22 07:00', samples: 38, pass: 31, fail: 7, avgFaithfulness: 0.82, status: 'warn' },
  { id: 'eval-004', time: '2026-05-21 07:00', samples: 45, pass: 38, fail: 7, avgFaithfulness: 0.84, status: 'pass' },
]

const promptVersions = [
  { hash: 'abc1234', template: 'pricing_objection', date: '2026-05-18', avgScore: 0.91, current: true },
  { hash: 'def5678', template: 'pricing_objection', date: '2026-05-10', avgScore: 0.87, current: false },
  { hash: 'ghi9012', template: 'timing_issue', date: '2026-05-15', avgScore: 0.89, current: true },
  { hash: 'jkl3456', template: 'ghosted', date: '2026-05-12', avgScore: 0.84, current: true },
]

const container = { hidden: {}, show: { transition: { staggerChildren: 0.07 } } }
const item = { hidden: { opacity: 0, y: 14 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }

function MetricGauge({ value, target, color }: { value: number; target: number; color: string }) {
  const pct = Math.round(value * 100)
  const targetPct = Math.round(target * 100)
  return (
    <div className="relative">
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <div className="h-2 rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <div className="absolute top-0 bottom-0 w-0.5 bg-white/30" style={{ left: `${targetPct}%` }} title={`Target: ${targetPct}%`} />
    </div>
  )
}

export default function AIQuality() {
  const [running, setRunning] = useState(false)

  function handleRun() {
    setRunning(true)
    setTimeout(() => setRunning(false), 3000)
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-400" />
            AI Quality Observability
          </h1>
          <p className="text-xs text-muted-foreground mt-0.5">RAGAS metrics, retrieval quality, and prompt evaluation</p>
        </div>
        <div className="flex items-center gap-2">
          <DemoLabel label="Sample Metrics" />
          <Button size="sm" variant="outline" className="gap-1.5" onClick={handleRun} disabled={running}>
            {running ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
            {running ? 'Running...' : 'Run Evaluation'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* Left Main (2 cols) */}
        <div className="col-span-2 space-y-4">
          {/* RAGAS Metric Cards */}
          <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-4 gap-3">
            {ragas.map(m => (
              <motion.div key={m.key} variants={item}>
                <Card className="relative overflow-hidden">
                  <CardContent className="p-4">
                    <div className="absolute top-2 right-2">
                      <DemoLabel label="Sample" />
                    </div>
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-1">{m.label}</p>
                    <p className="text-2xl font-bold text-foreground">{(m.value * 100).toFixed(0)}%</p>
                    <p className="text-[10px] text-green-400 mb-2">{m.trend} vs 4w ago</p>
                    <MetricGauge value={m.value} target={m.target} color={m.color} />
                    <div className="flex justify-between text-[10px] mt-1">
                      <span className="text-muted-foreground">Target: {Math.round(m.target * 100)}%</span>
                      <span style={{ color: m.color }} className="font-medium">
                        {m.value >= m.target ? '✓ Pass' : '✗ Fail'}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>

          {/* RAGAS Trend Chart */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">RAGAS Metric Trends</CardTitle>
                  <DemoLabel label="Sample Evaluation Data" />
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={chartData} margin={{ top: 5, right: 10, bottom: 0, left: -10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 32% 17%)" />
                    <XAxis dataKey="date" tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} />
                    <YAxis domain={[0.6, 1.0]} tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} tickFormatter={v => v.toFixed(2)} />
                    <Tooltip contentStyle={{ backgroundColor: 'hsl(222 47% 8%)', border: '1px solid hsl(217 32% 17%)', borderRadius: 6, fontSize: 11 }} />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                    <Line type="monotone" dataKey="Faithfulness" stroke="#3b82f6" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="Answer Rel." stroke="#22c55e" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="Ctx Recall" stroke="#f97316" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="Ctx Precision" stroke="#a855f7" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>

          {/* Failing Generations */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-400" />
                    <CardTitle className="text-sm">Failing Generations (Below Threshold)</CardTitle>
                  </div>
                  <DemoLabel label="Mock Eval" />
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left pb-2 text-muted-foreground font-medium">Generation ID</th>
                      <th className="text-left pb-2 text-muted-foreground font-medium">Lead</th>
                      <th className="text-left pb-2 text-muted-foreground font-medium">Faithfulness</th>
                      <th className="text-left pb-2 text-muted-foreground font-medium">Issue</th>
                      <th className="text-left pb-2 text-muted-foreground font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {failingGenerations.map(gen => (
                      <tr key={gen.id} className="border-b border-border last:border-0 hover:bg-muted/10">
                        <td className="py-2 font-mono text-[10px] text-muted-foreground">{gen.id}</td>
                        <td className="py-2 text-foreground font-medium">{gen.lead}</td>
                        <td className="py-2">
                          <span className="text-red-400 font-semibold">{(gen.faithfulness * 100).toFixed(0)}%</span>
                        </td>
                        <td className="py-2 text-muted-foreground max-w-[200px] truncate">{gen.issue}</td>
                        <td className="py-2">
                          <div className="flex items-center gap-1">
                            <Button size="sm" variant="ghost" className="h-6 px-2 text-[10px]">
                              <Eye className="h-3 w-3 mr-1" /> Review
                            </Button>
                            <Button size="sm" variant="ghost" className="h-6 px-2 text-[10px] text-red-400">
                              Drop
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          </motion.div>

          {/* Golden Dataset Coverage */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-sm font-semibold text-foreground">Golden Dataset Coverage</p>
                    <p className="text-xs text-muted-foreground mt-0.5">847 / 1,000 evaluation examples covered</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl font-bold text-foreground">84.7%</span>
                    <DemoLabel label="Sample" />
                  </div>
                </div>
                <div className="h-3 bg-muted rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: '84.7%' }}
                    transition={{ duration: 1, delay: 0.5, ease: 'easeOut' }}
                    className="h-3 bg-primary rounded-full"
                  />
                </div>
                <div className="flex justify-between text-[10px] mt-1.5 text-muted-foreground">
                  <span>847 examples covered</span>
                  <span>153 examples remaining</span>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Right Panel */}
        <div className="space-y-4">
          {/* Recent Evaluations */}
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-xs">Recent Evaluations</CardTitle>
                <DemoLabel label="Mock Eval" />
              </div>
            </CardHeader>
            <CardContent className="pt-0 space-y-2">
              {recentEvals.map(ev => (
                <div key={ev.id} className={cn("p-2.5 rounded border",
                  ev.status === 'pass' ? 'bg-green-500/5 border-green-500/20' : 'bg-yellow-500/5 border-yellow-500/20'
                )}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-mono text-muted-foreground">{ev.id}</span>
                    <span className={cn("text-[10px] font-medium",
                      ev.status === 'pass' ? 'text-green-400' : 'text-yellow-400'
                    )}>
                      {ev.status === 'pass' ? '✓ Pass' : '⚠ Warn'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                    <span>{ev.time.slice(5)}</span>
                    <span>{ev.pass}/{ev.samples} passed</span>
                    <span className="text-foreground font-medium">{(ev.avgFaithfulness * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Reranker Metrics */}
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <Zap className="h-3.5 w-3.5 text-blue-400" />
                  <CardTitle className="text-xs">Reranker Metrics</CardTitle>
                </div>
                <DemoLabel label="Sample" />
              </div>
            </CardHeader>
            <CardContent className="pt-0 space-y-2">
              <div className="text-[10px] text-muted-foreground mb-2">Cohere Rerank v3</div>
              {[
                { label: 'Avg Reranker Score', value: '0.84' },
                { label: 'Top-5 Precision', value: '91%' },
                { label: 'Avg Latency', value: '142ms' },
                { label: 'Reranks This Month', value: '4,218' },
                { label: 'Score Threshold', value: '0.60' },
              ].map(m => (
                <div key={m.label} className="flex justify-between">
                  <span className="text-[10px] text-muted-foreground">{m.label}</span>
                  <span className="text-xs font-medium text-foreground">{m.value}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Embedding Version */}
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-1.5">
                <Database className="h-3.5 w-3.5 text-purple-400" />
                <CardTitle className="text-xs">Embedding Version</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="pt-0 space-y-2">
              {[
                { label: 'Current Model', value: 'text-embedding-3-large' },
                { label: 'Dimensions', value: '3,072' },
                { label: 'Last Re-indexed', value: '2026-05-20' },
                { label: 'Total Vectors', value: '48,291' },
                { label: 'Index Status', value: 'Healthy ✓' },
              ].map(m => (
                <div key={m.label} className="flex justify-between">
                  <span className="text-[10px] text-muted-foreground">{m.label}</span>
                  <span className="text-[10px] font-medium text-foreground">{m.value}</span>
                </div>
              ))}
              <Button size="sm" variant="outline" className="w-full text-xs h-7 mt-2 gap-1">
                <RefreshCw className="h-3 w-3" /> Trigger Re-index
              </Button>
            </CardContent>
          </Card>

          {/* Prompt Version History */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs">Prompt Version History</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-2">
                {promptVersions.map(pv => (
                  <div key={pv.hash} className={cn("p-2 rounded border",
                    pv.current ? 'bg-primary/5 border-primary/20' : 'bg-muted/20 border-border'
                  )}>
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="text-[10px] font-mono text-muted-foreground">{pv.hash}</span>
                      {pv.current && <Badge variant="default" className="text-[9px] h-4 px-1">active</Badge>}
                    </div>
                    <p className="text-[10px] text-foreground font-medium">{pv.template}</p>
                    <div className="flex justify-between text-[10px] mt-0.5">
                      <span className="text-muted-foreground">{pv.date}</span>
                      <span className="text-green-400 font-medium">{(pv.avgScore * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
