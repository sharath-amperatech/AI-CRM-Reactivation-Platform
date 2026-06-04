import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Users, Calendar, TrendingUp, CheckCircle,
  Database, Search, Brain, MessageSquare, UserCheck, Send
} from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import SegmentBadge from '@/components/shared/SegmentBadge'
import DemoLabel from '@/components/shared/DemoLabel'
import {
  fetchCampaign, fetchCampaignEnrollments, fetchCampaignApprovals, pauseCampaign,
  type Campaign, type CampaignEnrollment, type CampaignApproval,
} from '@/lib/api'
import { cn, formatCurrency } from '@/lib/utils'

const statusColors: Record<string, string> = {
  active: 'bg-green-500/20 text-green-400 border-green-500/30',
  paused: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  completed: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  draft: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

const trendData = [
  { week: 'W1', opens: 41, replies: 12, meetings: 2 },
  { week: 'W2', opens: 58, replies: 15, meetings: 3 },
  { week: 'W3', opens: 63, replies: 19, meetings: 4 },
  { week: 'W4', opens: 68, replies: 22, meetings: 8 },
]

const stepDropoff = [
  { step: 'Email Sent', count: 47 },
  { step: 'Opened', count: 32 },
  { step: 'Clicked', count: 18 },
  { step: 'Replied', count: 10 },
  { step: 'Meeting', count: 8 },
  { step: 'Closed', count: 3 },
]

const workflowNodes = [
  { type: 'fetch_leads', label: 'Fetch Leads', icon: Database, status: 'complete', color: 'bg-blue-500/20 text-blue-400 border-blue-500/20' },
  { type: 'retrieve_context', label: 'Retrieve Context', icon: Search, status: 'complete', color: 'bg-purple-500/20 text-purple-400 border-purple-500/20' },
  { type: 'classify_lead', label: 'Classify Lead', icon: Brain, status: 'complete', color: 'bg-pink-500/20 text-pink-400 border-pink-500/20' },
  { type: 'generate_message', label: 'Generate Message', icon: MessageSquare, status: 'complete', color: 'bg-green-500/20 text-green-400 border-green-500/20' },
  { type: 'human_approval', label: 'Human Approval', icon: UserCheck, status: 'active', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/20' },
  { type: 'send_message', label: 'Send Message', icon: Send, status: 'pending', color: 'bg-muted text-muted-foreground border-border' },
]

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

export default function CampaignDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [enrollments, setEnrollments] = useState<CampaignEnrollment[]>([])
  const [approvals, setApprovals] = useState<CampaignApproval[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pausing, setPausing] = useState(false)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    Promise.all([
      fetchCampaign(id),
      fetchCampaignEnrollments(id),
      fetchCampaignApprovals(id),
    ])
      .then(([camp, enr, appr]) => {
        setCampaign(camp)
        setEnrollments(enr)
        setApprovals(appr)
        setError(null)
      })
      .catch(e => setError(e instanceof Error ? e.message : 'Failed to load campaign'))
      .finally(() => setLoading(false))
  }, [id])

  async function handlePause() {
    if (!id || !campaign) return
    setPausing(true)
    try {
      const updated = await pauseCampaign(id)
      setCampaign(updated)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to pause campaign')
    } finally {
      setPausing(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-8 bg-muted rounded w-1/3" />
        <div className="grid grid-cols-5 gap-3">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="h-16 bg-muted rounded" />)}</div>
        <div className="h-64 bg-muted rounded" />
      </div>
    )
  }

  if (error || !campaign) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <p className="text-sm text-destructive">{error ?? 'Campaign not found'}</p>
        <Button variant="outline" size="sm" onClick={() => navigate('/campaigns')}>Back to Campaigns</Button>
      </div>
    )
  }

  const steps = Array.from({ length: campaign.totalSteps }, (_, i) => ({
    n: i + 1,
    done: i < campaign.stepsCompleted,
  }))

  const meetingRate = campaign.enrolledLeads > 0
    ? Math.round(campaign.meetingsBooked / campaign.enrolledLeads * 100)
    : 0

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon-sm" onClick={() => navigate('/campaigns')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex items-center gap-2.5 flex-1 min-w-0">
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-lg font-bold text-foreground">{campaign.name}</h1>
              <span className={cn("inline-flex items-center px-2 py-0.5 rounded-md border text-[10px] font-medium", statusColors[campaign.status])}>
                {campaign.status}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-0.5">
              <SegmentBadge segment={campaign.segment} />
              {campaign.startedAt && (
                <span className="text-[10px] text-muted-foreground">Started {formatDate(campaign.startedAt)}</span>
              )}
              {campaign.abTest && <span className="text-[10px] text-purple-400 bg-purple-500/10 border border-purple-500/20 px-1.5 py-0.5 rounded">A/B Test</span>}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {campaign.status === 'active' && (
            <Button size="sm" variant="outline" className="gap-1.5 text-yellow-400 border-yellow-500/30" onClick={handlePause} disabled={pausing}>
              {pausing ? 'Pausing…' : 'Pause Campaign'}
            </Button>
          )}
          <Button size="sm" className="gap-1.5">
            <TrendingUp className="h-3.5 w-3.5" /> View Analytics
          </Button>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-5 gap-3">
        {[
          { label: 'Enrolled Leads', value: campaign.enrolledLeads, icon: Users },
          { label: 'Open Rate', value: `${campaign.openRate}%`, icon: TrendingUp },
          { label: 'Reply Rate', value: `${campaign.replyRate}%`, icon: TrendingUp },
          { label: 'Meetings Booked', value: campaign.meetingsBooked, icon: Calendar },
          { label: 'Revenue Recovered', value: formatCurrency(campaign.revenueRecovered), icon: CheckCircle },
        ].map(m => (
          <Card key={m.label}>
            <CardContent className="p-3 flex items-center gap-2">
              <m.icon className="h-4 w-4 text-primary shrink-0" />
              <div>
                <p className="text-[10px] text-muted-foreground">{m.label}</p>
                <p className="text-sm font-bold text-foreground">{m.value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <TabsList className="h-8">
          {['overview', 'workflow', 'leads', 'analytics', 'approvals'].map(t => (
            <TabsTrigger key={t} value={t} className="text-xs capitalize">{t}</TabsTrigger>
          ))}
        </TabsList>

        {/* Overview */}
        <TabsContent value="overview" className="mt-4 space-y-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-xs">Step Progress</CardTitle></CardHeader>
            <CardContent className="pt-0">
              <div className="flex items-center gap-2">
                {steps.map((s, i) => (
                  <div key={s.n} className="flex items-center gap-2 flex-1">
                    <div className={cn("w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border shrink-0",
                      s.done ? 'bg-green-500/20 text-green-400 border-green-500/30' : 'bg-muted text-muted-foreground border-border'
                    )}>
                      {s.done ? '✓' : s.n}
                    </div>
                    {i < steps.length - 1 && (
                      <div className={cn("h-0.5 flex-1", s.done ? 'bg-green-500/40' : 'bg-border')} />
                    )}
                  </div>
                ))}
                <span className="text-xs text-muted-foreground ml-2 shrink-0">{campaign.stepsCompleted}/{campaign.totalSteps} complete</span>
              </div>
            </CardContent>
          </Card>
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-xs">Campaign Details</CardTitle></CardHeader>
              <CardContent className="pt-0 space-y-2">
                {[
                  { label: 'Channel', value: campaign.channel },
                  { label: 'Created', value: formatDate(campaign.createdAt) },
                  { label: 'Started', value: formatDate(campaign.startedAt) },
                  { label: 'Converted Leads', value: campaign.convertedLeads },
                ].map(d => (
                  <div key={d.label} className="flex justify-between">
                    <span className="text-xs text-muted-foreground">{d.label}</span>
                    <span className="text-xs font-medium text-foreground capitalize">{d.value}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-xs">Conversion Rates</CardTitle></CardHeader>
              <CardContent className="pt-0 space-y-2">
                {[
                  { label: 'Open Rate', value: campaign.openRate },
                  { label: 'Reply Rate', value: campaign.replyRate },
                  { label: 'Meeting Rate', value: meetingRate },
                ].map(m => (
                  <div key={m.label}>
                    <div className="flex justify-between text-[10px] mb-0.5">
                      <span className="text-muted-foreground">{m.label}</span>
                      <span className="text-foreground font-medium">{m.value}%</span>
                    </div>
                    <div className="h-1.5 bg-muted rounded-full">
                      <div className="h-1.5 bg-primary rounded-full" style={{ width: `${m.value}%` }} />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Workflow */}
        <TabsContent value="workflow" className="mt-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-xs">Workflow Diagram (Read-only)</CardTitle>
                <Button size="sm" variant="outline" className="h-7 text-xs gap-1" onClick={() => navigate('/campaigns/new')}>
                  Edit Workflow
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="flex flex-col items-center gap-0 py-4">
                {workflowNodes.map((node, i) => (
                  <div key={node.type} className="flex flex-col items-center">
                    <div className={cn("flex items-center gap-2.5 px-4 py-2.5 rounded-lg border min-w-[220px]", node.color)}>
                      <node.icon className="h-4 w-4 shrink-0" />
                      <span className="text-xs font-medium">{node.label}</span>
                      <span className={cn("ml-auto text-[10px] px-1.5 py-0.5 rounded",
                        node.status === 'complete' ? 'bg-green-500/20 text-green-400' :
                        node.status === 'active' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-muted text-muted-foreground'
                      )}>
                        {node.status}
                      </span>
                    </div>
                    {i < workflowNodes.length - 1 && (
                      <div className="w-0.5 h-6 bg-border/60" />
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Enrolled Leads */}
        <TabsContent value="leads" className="mt-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs">Enrolled Leads ({enrollments.length})</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              {enrollments.length === 0 && (
                <p className="text-xs text-muted-foreground py-4">No leads enrolled in this campaign yet.</p>
              )}
              <div className="space-y-2">
                {enrollments.map(enrollment => (
                  <div key={enrollment.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-[10px] font-bold text-primary">{enrollment.lead.name[0]}</div>
                      <div>
                        <p className="text-xs font-medium text-foreground">{enrollment.lead.name}</p>
                        <p className="text-[10px] text-muted-foreground">{enrollment.lead.company}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] text-muted-foreground">Step {enrollment.currentStep}/{campaign.totalSteps}</span>
                      <SegmentBadge segment={enrollment.lead.segment} />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics */}
        <TabsContent value="analytics" className="mt-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xs">Engagement Trend</CardTitle>
                  <DemoLabel />
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <ResponsiveContainer width="100%" height={160}>
                  <LineChart data={trendData} margin={{ top: 5, right: 5, bottom: 0, left: -20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 32% 17%)" />
                    <XAxis dataKey="week" tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} />
                    <YAxis tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} />
                    <Tooltip contentStyle={{ backgroundColor: 'hsl(222 47% 8%)', border: '1px solid hsl(217 32% 17%)', borderRadius: 6, fontSize: 11 }} />
                    <Line type="monotone" dataKey="opens" stroke="#3b82f6" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="replies" stroke="#22c55e" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="meetings" stroke="#f97316" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xs">Step Drop-off Funnel</CardTitle>
                  <DemoLabel />
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart layout="vertical" data={stepDropoff} margin={{ top: 0, right: 30, bottom: 0, left: 0 }}>
                    <XAxis type="number" tick={{ fontSize: 10, fill: 'hsl(215 20% 55%)' }} />
                    <YAxis dataKey="step" type="category" tick={{ fontSize: 9, fill: 'hsl(215 20% 55%)' }} width={65} />
                    <Tooltip contentStyle={{ backgroundColor: 'hsl(222 47% 8%)', border: '1px solid hsl(217 32% 17%)', borderRadius: 6, fontSize: 11 }} />
                    <Bar dataKey="count" fill="#3b82f6" radius={[0, 3, 3, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Approvals */}
        <TabsContent value="approvals" className="mt-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-xs">Approval History</CardTitle></CardHeader>
            <CardContent className="pt-0">
              {approvals.length === 0 && (
                <p className="text-xs text-muted-foreground py-4">No approvals found for this campaign.</p>
              )}
              <div className="space-y-2">
                {approvals.map(a => (
                  <div key={a.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                    <div>
                      <p className="text-xs font-medium text-foreground">{a.leadName ?? '—'}</p>
                      <p className="text-[10px] text-muted-foreground">{a.company ?? '—'}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-green-400">{Math.round(a.confidence * 100)}%</span>
                      <span className={cn("text-[10px] px-1.5 py-0.5 rounded border",
                        a.status === 'pending' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                        a.status === 'approved' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                        'bg-red-500/10 text-red-400 border-red-500/20'
                      )}>
                        {a.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
