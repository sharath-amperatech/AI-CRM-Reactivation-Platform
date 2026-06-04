import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CheckCircle, XCircle, Edit3, Mail, MessageSquare,
  ExternalLink, ChevronDown, ChevronUp, Zap, Users,
  Brain, Database, AlertCircle, Loader2
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import DemoLabel from '@/components/shared/DemoLabel'
import SegmentBadge from '@/components/shared/SegmentBadge'
import ConfidenceBar from '@/components/shared/ConfidenceBar'
import {
  fetchApprovals,
  approveApproval,
  rejectApproval,
  editAndApproveApproval,
  bulkApproveHighConfidence,
  type Approval,
} from '@/lib/api'
import { cn, formatCurrency } from '@/lib/utils'

const channelIcons: Record<string, React.ElementType> = {
  email: Mail,
  sms: MessageSquare,
  whatsapp: MessageSquare,
}

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

export default function Approvals() {
  const [approvals, setApprovals] = useState<Approval[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<Approval | null>(null)
  const [editMode, setEditMode] = useState(false)
  const [editedBody, setEditedBody] = useState('')
  const [contextExpanded, setContextExpanded] = useState(false)
  const [reasoningExpanded, setReasoningExpanded] = useState(true)
  const [chunksExpanded, setChunksExpanded] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    loadApprovals()
  }, [])

  async function loadApprovals() {
    setLoading(true)
    setError(null)
    try {
      const { approvals: data } = await fetchApprovals()
      setApprovals(data)
      if (data.length > 0 && !selected) {
        setSelected(data[0])
        setEditedBody(data[0].messageBody)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load approvals')
    } finally {
      setLoading(false)
    }
  }

  const pending = approvals.filter(a => a.status === 'pending')
  const highConfidence = pending.filter(a => a.confidence >= 0.85)

  async function handleApprove(id: string) {
    setActionLoading(true)
    try {
      const updated = await approveApproval(id)
      setApprovals(prev => prev.map(a => a.id === id ? updated : a))
      const next = pending.find(a => a.id !== id)
      if (next) selectApproval(next)
    } finally {
      setActionLoading(false)
    }
  }

  async function handleReject(id: string) {
    setActionLoading(true)
    try {
      const updated = await rejectApproval(id)
      setApprovals(prev => prev.map(a => a.id === id ? updated : a))
      const next = pending.find(a => a.id !== id)
      if (next) selectApproval(next)
    } finally {
      setActionLoading(false)
    }
  }

  async function handleEditAndApprove(id: string, body: string) {
    setActionLoading(true)
    try {
      const updated = await editAndApproveApproval(id, body)
      setApprovals(prev => prev.map(a => a.id === id ? updated : a))
      setEditMode(false)
      const next = pending.find(a => a.id !== id)
      if (next) selectApproval(next)
    } finally {
      setActionLoading(false)
    }
  }

  async function handleBulkApproveHighConfidence() {
    setActionLoading(true)
    try {
      await bulkApproveHighConfidence(0.85)
      await loadApprovals()
    } finally {
      setActionLoading(false)
    }
  }

  function selectApproval(a: Approval) {
    setSelected(a)
    setEditMode(false)
    setEditedBody(a.messageBody)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <Card className="max-w-sm w-full">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-8 w-8 text-red-400 mx-auto mb-3" />
            <p className="text-sm font-medium text-foreground mb-1">Failed to load approvals</p>
            <p className="text-xs text-muted-foreground mb-4">{error}</p>
            <Button size="sm" onClick={loadApprovals}>Retry</Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (approvals.length === 0) {
    return (
      <div className="flex flex-col h-full space-y-4">
        <div>
          <h1 className="text-xl font-bold text-foreground">Approval Inbox</h1>
          <p className="text-xs text-muted-foreground mt-0.5">0 pending</p>
        </div>
        <div className="flex items-center justify-center flex-1">
          <div className="text-center">
            <CheckCircle className="h-10 w-10 text-green-400 mx-auto mb-3" />
            <p className="text-sm font-medium text-foreground">All caught up</p>
            <p className="text-xs text-muted-foreground mt-1">No pending approvals at this time.</p>
          </div>
        </div>
      </div>
    )
  }

  const activeSelected = selected ? (approvals.find(a => a.id === selected.id) ?? selected) : approvals[0]
  const ChanIcon = channelIcons[activeSelected.channel] || Mail
  const currentStatus = activeSelected.status

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-xl font-bold text-foreground">Approval Inbox</h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            {pending.length} pending · {highConfidence.length} high-confidence
          </p>
        </div>
        {highConfidence.length > 0 && (
          <Button
            size="sm"
            className="gap-1.5 bg-green-600 hover:bg-green-700"
            onClick={handleBulkApproveHighConfidence}
            disabled={actionLoading}
          >
            {actionLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Zap className="h-3.5 w-3.5" />}
            Approve All High Confidence (&gt;85%) — {highConfidence.length} items
          </Button>
        )}
      </div>

      <div className="flex gap-4 flex-1 min-h-0">
        {/* Left Panel — Approval List */}
        <div className="w-80 flex flex-col gap-2 overflow-y-auto scrollbar-thin shrink-0">
          {approvals.map(a => {
            const CIcon = channelIcons[a.channel] || Mail
            return (
              <motion.div
                key={a.id}
                layout
                onClick={() => selectApproval(a)}
                className={cn(
                  "p-3 rounded-lg border cursor-pointer transition-all",
                  activeSelected.id === a.id
                    ? "border-primary/40 bg-primary/5 shadow-sm"
                    : "border-border bg-card hover:border-border/80 hover:bg-muted/20",
                  a.status !== 'pending' && "opacity-60"
                )}
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-[10px] font-bold text-primary shrink-0">
                      {a.leadName?.[0]?.toUpperCase() ?? '?'}
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs font-medium text-foreground truncate">{a.leadName || 'Unknown Lead'}</p>
                      <p className="text-[10px] text-muted-foreground truncate">{a.company || '—'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 shrink-0">
                    <CIcon className="h-3 w-3 text-muted-foreground" />
                    <span className={cn(
                      "text-[10px] px-1 py-0.5 rounded border font-medium",
                      a.status === 'pending' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                      a.status === 'approved' || a.status === 'edited' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                      'bg-red-500/10 text-red-400 border-red-500/20'
                    )}>
                      {a.status}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <SegmentBadge segment={a.segment} />
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-green-400">{Math.round(a.confidence * 100)}%</span>
                    <span className="text-[10px] text-muted-foreground">{timeAgo(a.createdAt)}</span>
                  </div>
                </div>
                <p className="text-[10px] text-muted-foreground mt-1.5 truncate">{a.campaignName}</p>
              </motion.div>
            )
          })}
        </div>

        {/* Right Panel — Full Approval Card */}
        <div className="flex-1 overflow-y-auto scrollbar-thin">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeSelected.id}
              initial={{ opacity: 0, x: 12 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -12 }}
              transition={{ duration: 0.2 }}
              className="space-y-3"
            >
              {/* Top card */}
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3 min-w-0">
                      <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-sm font-bold text-primary shrink-0">
                        {activeSelected.leadName?.[0]?.toUpperCase() ?? '?'}
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h2 className="text-base font-bold text-foreground">{activeSelected.leadName || 'Unknown Lead'}</h2>
                          <SegmentBadge segment={activeSelected.segment} />
                        </div>
                        <p className="text-xs text-muted-foreground">{activeSelected.company || '—'}</p>
                        <div className="flex items-center gap-3 mt-2">
                          <div className="flex items-center gap-1.5">
                            <span className="text-[10px] text-muted-foreground">Confidence:</span>
                            <div className="w-24">
                              <ConfidenceBar value={activeSelected.confidence} />
                            </div>
                          </div>
                          <span className="text-[10px] text-muted-foreground">Deal: <span className="text-foreground font-medium">{formatCurrency(activeSelected.dealValue)}</span></span>
                          <span className="text-[10px] text-muted-foreground">via <span className="text-foreground font-medium capitalize">{activeSelected.channel}</span></span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="text-[10px] text-muted-foreground">{activeSelected.campaignName}</p>
                      <p className="text-[10px] text-muted-foreground mt-0.5">{timeAgo(activeSelected.createdAt)}</p>
                      {currentStatus !== 'pending' && (
                        <span className={cn("inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded border mt-1 font-medium",
                          currentStatus === 'approved' || currentStatus === 'edited' ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'
                        )}>
                          {currentStatus === 'approved' || currentStatus === 'edited' ? <CheckCircle className="h-2.5 w-2.5" /> : <XCircle className="h-2.5 w-2.5" />}
                          {currentStatus}
                        </span>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Langfuse Trace Link */}
              {activeSelected.traceId && (
                <div className="flex items-center gap-2 px-1">
                  <span className="text-[10px] text-muted-foreground">Trace ID:</span>
                  <a
                    href={`https://langfuse.com/trace/${activeSelected.traceId}`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-[10px] font-mono text-primary hover:underline"
                  >
                    {activeSelected.traceId}
                    <ExternalLink className="h-2.5 w-2.5" />
                  </a>
                </div>
              )}

              {/* CRM Context */}
              {activeSelected.crmContext && (
                <Card>
                  <button
                    className="w-full flex items-center justify-between px-4 py-3"
                    onClick={() => setContextExpanded(!contextExpanded)}
                  >
                    <div className="flex items-center gap-2">
                      <Database className="h-3.5 w-3.5 text-muted-foreground" />
                      <span className="text-xs font-semibold text-foreground">CRM Context</span>
                    </div>
                    {contextExpanded ? <ChevronUp className="h-3.5 w-3.5 text-muted-foreground" /> : <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />}
                  </button>
                  <AnimatePresence>
                    {contextExpanded && (
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: 'auto' }}
                        exit={{ height: 0 }}
                        className="overflow-hidden"
                      >
                        <CardContent className="pt-0 pb-4 px-4">
                          <div className="space-y-2">
                            {(() => {
                              const headerRe = /^\[(\d+)\]\s+\(([^—]+?)—\s*([^)]+)\)\s+\[(\w+)\]/
                              const blocks = activeSelected.crmContext.split(/\n\n+/)
                              const parsed = blocks.map(block => {
                                const nl = block.indexOf('\n')
                                const headerLine = nl === -1 ? block : block.slice(0, nl)
                                const content = nl === -1 ? '' : block.slice(nl + 1).trim()
                                const m = headerLine.match(headerRe)
                                if (!m) return { raw: block }
                                return { index: m[1], type: m[2].trim(), date: m[3].trim(), label: m[4], content }
                              })
                              const allParsed = parsed.every(e => !('raw' in e))
                              if (!allParsed) {
                                return (
                                  <p className="text-xs text-muted-foreground leading-relaxed border-l-2 border-primary/30 pl-3">
                                    {activeSelected.crmContext}
                                  </p>
                                )
                              }
                              return parsed.map((entry, i) => (
                                <div key={i} className="rounded border border-border bg-muted/20 p-2">
                                  <div className="flex flex-wrap items-center gap-1.5 mb-1">
                                    <span className="text-[10px] font-bold text-primary">[{(entry as any).index}]</span>
                                    <span className="text-[10px] font-medium text-foreground capitalize">{(entry as any).type}</span>
                                    <span className="text-[10px] text-muted-foreground">·</span>
                                    <span className="text-[10px] text-muted-foreground">{(entry as any).date}</span>
                                    <span className="text-[10px] bg-primary/10 text-primary rounded px-1">{(entry as any).label}</span>
                                  </div>
                                  <p className="text-[10px] text-muted-foreground leading-relaxed">{(entry as any).content}</p>
                                </div>
                              ))
                            })()}
                          </div>
                        </CardContent>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </Card>
              )}

              {/* AI Reasoning */}
              {activeSelected.aiReasoning && (
                <Card>
                  <button
                    className="w-full flex items-center justify-between px-4 py-3"
                    onClick={() => setReasoningExpanded(!reasoningExpanded)}
                  >
                    <div className="flex items-center gap-2">
                      <Brain className="h-3.5 w-3.5 text-purple-400" />
                      <span className="text-xs font-semibold text-foreground">AI Reasoning</span>
                      <DemoLabel label="AI-generated" />
                    </div>
                    {reasoningExpanded ? <ChevronUp className="h-3.5 w-3.5 text-muted-foreground" /> : <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />}
                  </button>
                  <AnimatePresence>
                    {reasoningExpanded && (
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: 'auto' }}
                        exit={{ height: 0 }}
                        className="overflow-hidden"
                      >
                        <CardContent className="pt-0 pb-4 px-4">
                          <p className="text-xs text-muted-foreground leading-relaxed">{activeSelected.aiReasoning}</p>
                        </CardContent>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </Card>
              )}

              {/* Retrieved Chunks */}
              {activeSelected.retrievedChunks.length > 0 && (
                <Card>
                  <button
                    className="w-full flex items-center justify-between px-4 py-3"
                    onClick={() => setChunksExpanded(!chunksExpanded)}
                  >
                    <div className="flex items-center gap-2">
                      <Database className="h-3.5 w-3.5 text-blue-400" />
                      <span className="text-xs font-semibold text-foreground">Retrieved Chunks ({activeSelected.retrievedChunks.length})</span>
                    </div>
                    {chunksExpanded ? <ChevronUp className="h-3.5 w-3.5 text-muted-foreground" /> : <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />}
                  </button>
                  <AnimatePresence>
                    {chunksExpanded && (
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: 'auto' }}
                        exit={{ height: 0 }}
                        className="overflow-hidden"
                      >
                        <CardContent className="pt-0 pb-4 px-4 space-y-2">
                          {activeSelected.retrievedChunks.map((chunk, i) => (
                            <div key={i} className="flex items-start gap-2 bg-muted/30 rounded p-2">
                              <span className="text-[10px] font-bold text-primary shrink-0 mt-0.5">{i + 1}</span>
                              <p className="text-[10px] text-muted-foreground leading-relaxed">{chunk}</p>
                            </div>
                          ))}
                        </CardContent>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </Card>
              )}

              {/* Generated Message */}
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <ChanIcon className="h-3.5 w-3.5 text-muted-foreground" />
                      <CardTitle className="text-xs">Generated Message</CardTitle>
                    </div>
                    <div className="flex items-center gap-2">
                      <DemoLabel label="AI Draft" />
                      {currentStatus === 'pending' && (
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 text-xs gap-1"
                          onClick={() => {
                            setEditMode(!editMode)
                            if (!editMode) setEditedBody(activeSelected.messageBody)
                          }}
                        >
                          <Edit3 className="h-3 w-3" />
                          {editMode ? 'Cancel Edit' : 'Edit'}
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0 space-y-3">
                  {/* Subject */}
                  {activeSelected.subject && (
                    <div className="bg-muted/30 rounded p-2">
                      <p className="text-[10px] text-muted-foreground mb-0.5 uppercase tracking-wide">Subject</p>
                      <p className="text-xs font-medium text-foreground">{activeSelected.subject}</p>
                    </div>
                  )}

                  {/* Body */}
                  {editMode ? (
                    <textarea
                      value={editedBody}
                      onChange={e => setEditedBody(e.target.value)}
                      className="w-full h-64 bg-muted/30 border border-border rounded p-3 text-xs text-foreground leading-relaxed resize-none focus:outline-none focus:ring-1 focus:ring-ring scrollbar-thin font-sans"
                    />
                  ) : (
                    <div className="bg-muted/30 rounded p-3 max-h-64 overflow-y-auto scrollbar-thin">
                      <pre className="text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap font-sans">{activeSelected.messageBody}</pre>
                    </div>
                  )}

                  {/* Confidence indicator */}
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-3 w-3 text-muted-foreground" />
                    <span className="text-[10px] text-muted-foreground">
                      AI confidence: <span className={cn("font-semibold", activeSelected.confidence >= 0.85 ? 'text-green-400' : activeSelected.confidence >= 0.70 ? 'text-yellow-400' : 'text-red-400')}>
                        {Math.round(activeSelected.confidence * 100)}%
                      </span>
                    </span>
                  </div>

                  {/* Action buttons */}
                  {currentStatus === 'pending' && (
                    <div className="flex items-center gap-2 pt-1 border-t border-border">
                      <Button
                        size="sm"
                        className="gap-1.5 bg-green-600 hover:bg-green-700 flex-1"
                        onClick={() => handleApprove(activeSelected.id)}
                        disabled={actionLoading}
                      >
                        {actionLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <CheckCircle className="h-3.5 w-3.5" />}
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="gap-1.5 flex-1"
                        onClick={() => setEditMode(true)}
                        disabled={actionLoading}
                      >
                        <Edit3 className="h-3.5 w-3.5" />
                        Edit &amp; Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="gap-1.5 text-red-400 border-red-500/30 hover:bg-red-500/10"
                        onClick={() => handleReject(activeSelected.id)}
                        disabled={actionLoading}
                      >
                        <XCircle className="h-3.5 w-3.5" />
                        Reject
                      </Button>
                      <Button size="sm" variant="ghost" className="gap-1.5 text-muted-foreground" disabled={actionLoading}>
                        <Users className="h-3.5 w-3.5" /> Reassign
                      </Button>
                    </div>
                  )}
                  {currentStatus !== 'pending' && (
                    <div className={cn("flex items-center gap-2 px-3 py-2 rounded border text-xs font-medium",
                      currentStatus === 'approved' || currentStatus === 'edited' ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'
                    )}>
                      {currentStatus === 'approved' || currentStatus === 'edited' ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
                      This message has been {currentStatus}.
                    </div>
                  )}

                  {editMode && currentStatus === 'pending' && (
                    <Button
                      size="sm"
                      className="w-full gap-1.5 bg-blue-600 hover:bg-blue-700"
                      onClick={() => handleEditAndApprove(activeSelected.id, editedBody)}
                      disabled={actionLoading}
                    >
                      {actionLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <CheckCircle className="h-3.5 w-3.5" />}
                      Save Edits &amp; Approve
                    </Button>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
