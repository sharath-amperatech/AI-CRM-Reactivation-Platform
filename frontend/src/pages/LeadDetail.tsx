import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  ArrowLeft, Mail, Phone, MapPin, Building2, Briefcase,
  Zap, MessageSquare, PlusCircle, CheckCircle, XCircle,
  Calendar, FileText, PhoneCall, Edit3,
  ThumbsUp, ThumbsDown, Minus
} from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import SegmentBadge from '@/components/shared/SegmentBadge'
import ConfidenceBar from '@/components/shared/ConfidenceBar'
import DemoLabel from '@/components/shared/DemoLabel'
import { statusColors, type Lead, type CRMActivity } from '@/data/mockData'
import { cn, formatCurrency, getRelativeTime } from '@/lib/utils'
import {
  fetchLead,
  fetchLeadActivities,
  fetchLeadMessages,
  fetchLeadAuditLogs,
  type LeadMessage,
  type LeadAuditLog,
} from '@/lib/api'

const activityIcons: Record<string, React.ElementType> = {
  email: Mail,
  call: PhoneCall,
  meeting: Calendar,
  note: FileText,
  deal_update: Zap,
}

const sentimentConfig = {
  positive: { icon: ThumbsUp, color: 'text-green-400', label: 'Positive' },
  neutral: { icon: Minus, color: 'text-muted-foreground', label: 'Neutral' },
  negative: { icon: ThumbsDown, color: 'text-red-400', label: 'Negative' },
}

export default function LeadDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [lead, setLead] = useState<Lead | null>(null)
  const [activities, setActivities] = useState<CRMActivity[]>([])
  const [messages, setMessages] = useState<LeadMessage[]>([])
  const [auditLogs, setAuditLogs] = useState<LeadAuditLog[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    Promise.allSettled([
      fetchLead(id),
      fetchLeadActivities(id),
      fetchLeadMessages(id),
      fetchLeadAuditLogs(id),
    ])
      .then(([l, acts, msgs, logs]) => {
        if (l.status === 'fulfilled') setLead(l.value)
        if (acts.status === 'fulfilled') setActivities(acts.value)
        if (msgs.status === 'fulfilled') setMessages(msgs.value)
        if (logs.status === 'fulfilled') setAuditLogs(logs.value)
      })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">
        Loading lead...
      </div>
    )
  }

  if (!lead) {
    return (
      <div className="flex items-center justify-center py-24 text-sm text-muted-foreground">
        Lead not found.
      </div>
    )
  }

  const latestChunks = messages[0]?.retrievedChunks ?? []
  const avgSimilarity =
    latestChunks.length > 0
      ? (latestChunks.reduce((s, c) => s + c.score, 0) / latestChunks.length).toFixed(2)
      : null

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon-sm" onClick={() => navigate('/leads')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex items-center gap-2.5 flex-1 min-w-0">
          <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-sm font-bold text-primary shrink-0">
            {lead.name[0]}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-lg font-bold text-foreground">{lead.name}</h1>
              <SegmentBadge segment={lead.segment} />
              <span className={cn("inline-flex items-center px-2 py-0.5 rounded-md border text-[10px] font-medium", statusColors[lead.status])}>
                {lead.status.replace('_', ' ')}
              </span>
            </div>
            <p className="text-xs text-muted-foreground">{lead.role} · {lead.company}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Button size="sm" variant="outline" className="gap-1.5">
            <PlusCircle className="h-3.5 w-3.5" /> Add to Campaign
          </Button>
          <Button size="sm" className="gap-1.5">
            <MessageSquare className="h-3.5 w-3.5" /> Generate Message
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-4 gap-4">
        {/* Left Panel */}
        <div className="space-y-3">
          {/* Contact Info */}
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-xs">Contact Info</CardTitle></CardHeader>
            <CardContent className="pt-0 space-y-2">
              {[
                { icon: Mail, label: lead.email },
                { icon: Phone, label: lead.phone },
                { icon: MapPin, label: lead.location },
                { icon: Building2, label: `${lead.company} · ${lead.companySize}` },
                { icon: Briefcase, label: lead.industry },
              ].map(({ icon: Icon, label }, i) => (
                <div key={i} className="flex items-start gap-2">
                  <Icon className="h-3.5 w-3.5 text-muted-foreground mt-0.5 shrink-0" />
                  <span className="text-xs text-muted-foreground break-all">{label}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* AI Classification */}
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-xs">AI Classification</CardTitle>
                <DemoLabel label="AI" />
              </div>
            </CardHeader>
            <CardContent className="pt-0 space-y-2">
              <div><p className="text-[10px] text-muted-foreground mb-1">Segment</p><SegmentBadge segment={lead.segment} /></div>
              <div>
                <p className="text-[10px] text-muted-foreground mb-1">Confidence</p>
                <ConfidenceBar value={lead.confidence} />
              </div>
              <div className="text-[10px] text-muted-foreground bg-muted/30 rounded p-2 leading-relaxed">
                {messages[0]?.aiReasoning ?? 'No AI reasoning available for this lead.'}
              </div>
            </CardContent>
          </Card>

          {/* Deal Info */}
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-xs">Deal Info</CardTitle></CardHeader>
            <CardContent className="pt-0 space-y-2">
              {[
                { label: 'Deal Value', value: formatCurrency(lead.dealValue) },
                { label: 'Source', value: lead.source },
                { label: 'Assigned To', value: lead.assignedTo },
                { label: 'Inactive Days', value: lead.inactiveDays === 0 ? 'Active' : `${lead.inactiveDays} days` },
                { label: 'Campaigns', value: lead.campaigns.length > 0 ? lead.campaigns.join(', ') : 'None' },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between items-center">
                  <span className="text-[10px] text-muted-foreground">{label}</span>
                  <span className="text-xs font-medium text-foreground">{value}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Right Tabs */}
        <div className="col-span-3">
          <Tabs defaultValue="overview">
            <TabsList className="mb-4 h-8">
              {['overview', 'activity', 'context', 'messages', 'workflow', 'audit'].map(t => (
                <TabsTrigger key={t} value={t} className="text-xs capitalize">
                  {t === 'context' ? 'AI Context' : t === 'messages' ? 'Generated Msgs' : t === 'workflow' ? 'Workflow' : t}
                </TabsTrigger>
              ))}
            </TabsList>

            {/* Overview */}
            <TabsContent value="overview">
              <div className="space-y-3">
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-xs">CRM Summary</CardTitle></CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-xs text-muted-foreground italic">
                      {lead.crmSummary ?? 'No summary available.'}
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-xs">Recent Activity Summary</CardTitle></CardHeader>
                  <CardContent className="pt-0 space-y-2">
                    {activities.slice(0, 3).map(a => (
                      <div key={a.id} className="flex items-start gap-2 text-xs">
                        <span className="text-muted-foreground whitespace-nowrap">{getRelativeTime(a.date)}</span>
                        <span className="text-foreground">{a.summary}</span>
                      </div>
                    ))}
                    {activities.length === 0 && <p className="text-xs text-muted-foreground">No activities recorded.</p>}
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2"><CardTitle className="text-xs">Tags</CardTitle></CardHeader>
                  <CardContent className="pt-0">
                    <div className="flex flex-wrap gap-1.5">
                      {lead.tags.map(tag => (
                        <Badge key={tag} variant="secondary" className="text-[10px]">{tag}</Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* CRM Activity */}
            <TabsContent value="activity">
              <div className="space-y-2">
                {activities.length === 0 && (
                  <Card><CardContent className="py-8 text-center text-xs text-muted-foreground">No CRM activities recorded for this lead.</CardContent></Card>
                )}
                {activities.map(a => {
                  const Icon = activityIcons[a.type] || FileText
                  const sent = sentimentConfig[a.sentiment]
                  return (
                    <motion.div key={a.id} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}>
                      <Card>
                        <CardContent className="p-4">
                          <div className="flex items-start gap-3">
                            <div className="w-7 h-7 rounded-full bg-muted flex items-center justify-center shrink-0">
                              <Icon className="h-3.5 w-3.5 text-muted-foreground" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap mb-1">
                                <span className="text-xs font-medium text-foreground capitalize">{a.type.replace('_', ' ')}</span>
                                <span className="text-[10px] text-muted-foreground">{getRelativeTime(a.date)}</span>
                                <span className="text-[10px] text-muted-foreground">· {a.author}</span>
                                <sent.icon className={cn("h-3 w-3 ml-auto", sent.color)} />
                              </div>
                              <p className="text-xs font-medium text-foreground mb-1">{a.summary}</p>
                              <p className="text-xs text-muted-foreground leading-relaxed">{a.content}</p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  )
                })}
              </div>
            </TabsContent>

            {/* AI Context */}
            <TabsContent value="context">
              <div className="space-y-2">
                {latestChunks.length === 0 ? (
                  <Card>
                    <CardContent className="py-8 text-center text-xs text-muted-foreground">
                      No RAG context available. Generate a message to populate context chunks.
                    </CardContent>
                  </Card>
                ) : (
                  <>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs text-muted-foreground">
                        {latestChunks.length} chunk{latestChunks.length !== 1 ? 's' : ''} retrieved
                        {avgSimilarity ? ` · avg similarity: ${avgSimilarity}` : ''}
                      </p>
                    </div>
                    {latestChunks.map((chunk, idx) => (
                      <Card key={idx}>
                        <CardContent className="p-3">
                          <div className="flex items-start justify-between gap-2 mb-1.5">
                            <span className="text-[10px] font-mono bg-muted px-1.5 py-0.5 rounded text-muted-foreground">{chunk.source}</span>
                            <div className="flex items-center gap-2 shrink-0">
                              <span className="text-[10px] text-muted-foreground">sim: <span className="text-foreground font-medium">{chunk.score}</span></span>
                              <span className="text-[10px] text-muted-foreground">rerank: <span className="text-foreground font-medium">{chunk.reranker}</span></span>
                            </div>
                          </div>
                          <p className="text-xs text-muted-foreground leading-relaxed">{chunk.text}</p>
                        </CardContent>
                      </Card>
                    ))}
                  </>
                )}
              </div>
            </TabsContent>

            {/* Generated Messages */}
            <TabsContent value="messages">
              <div className="space-y-3">
                {messages.length === 0 && (
                  <Card>
                    <CardContent className="py-8 text-center text-xs text-muted-foreground">
                      No generated messages for this lead.
                    </CardContent>
                  </Card>
                )}
                {messages.map(msg => (
                  <Card key={msg.id}>
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-[10px] text-muted-foreground mb-0.5">Subject</p>
                          <p className="text-xs font-medium text-foreground">{msg.subject ?? '(no subject)'}</p>
                        </div>
                        <div className="flex items-center gap-1.5 shrink-0">
                          <Badge variant="outline" className="text-[10px]">{msg.channel}</Badge>
                          <span className="text-[10px] text-green-400 font-medium">{Math.round(msg.confidence * 100)}% confidence</span>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="bg-muted/30 rounded-md p-3 mb-3">
                        <pre className="text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap font-sans">{msg.body}</pre>
                      </div>
                      {msg.approvalStatus === 'pending' ? (
                        <div className="flex items-center gap-2">
                          <Button size="sm" className="gap-1.5 bg-green-600 hover:bg-green-700">
                            <CheckCircle className="h-3.5 w-3.5" /> Approve
                          </Button>
                          <Button size="sm" variant="outline" className="gap-1.5">
                            <Edit3 className="h-3.5 w-3.5" /> Edit &amp; Approve
                          </Button>
                          <Button size="sm" variant="outline" className="gap-1.5 text-red-400 border-red-500/30 hover:bg-red-500/10">
                            <XCircle className="h-3.5 w-3.5" /> Reject
                          </Button>
                        </div>
                      ) : msg.approvalStatus ? (
                        <Badge variant="outline" className="text-[10px] capitalize">{msg.approvalStatus}</Badge>
                      ) : null}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Workflow History */}
            <TabsContent value="workflow">
              <Card>
                <CardContent className="py-8 text-center text-xs text-muted-foreground">
                  Workflow execution history is not yet persisted. Step logs will appear here once
                  workflow step tracking is implemented.
                </CardContent>
              </Card>
            </TabsContent>

            {/* Audit Trail */}
            <TabsContent value="audit">
              <Card>
                {auditLogs.length === 0 ? (
                  <CardContent className="py-8 text-center text-xs text-muted-foreground">
                    No audit events recorded for this lead.
                  </CardContent>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-border bg-muted/30">
                          <th className="text-left px-4 py-2.5 text-muted-foreground font-medium">Action</th>
                          <th className="text-left px-4 py-2.5 text-muted-foreground font-medium">User</th>
                          <th className="text-left px-4 py-2.5 text-muted-foreground font-medium">Time</th>
                          <th className="text-left px-4 py-2.5 text-muted-foreground font-medium">Resource</th>
                        </tr>
                      </thead>
                      <tbody>
                        {auditLogs.map(row => (
                          <tr key={row.id} className="border-b border-border hover:bg-muted/10">
                            <td className="px-4 py-2.5 text-foreground">{row.action}</td>
                            <td className="px-4 py-2.5 text-muted-foreground">{row.userName ?? 'System'}</td>
                            <td className="px-4 py-2.5 text-muted-foreground whitespace-nowrap">{new Date(row.createdAt).toLocaleString()}</td>
                            <td className="px-4 py-2.5 text-muted-foreground font-mono">
                              {row.resourceType}{row.resourceId ? `:${row.resourceId.slice(0, 8)}` : ''}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
