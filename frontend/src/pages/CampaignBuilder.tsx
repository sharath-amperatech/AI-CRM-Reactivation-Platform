import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Database, Search, Brain, MessageSquare, UserCheck,
  Send, Clock, BarChart3, Calendar, AlertTriangle,
  ArrowLeft, Save, Rocket, X, Settings2, Loader2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import { createCampaign, launchCampaign } from '@/lib/api'

interface NodeType {
  type: string
  label: string
  icon: React.ElementType
  description: string
  color: string
  bgColor: string
}

const nodeTypes: NodeType[] = [
  { type: 'fetch_leads', label: 'Fetch Leads', icon: Database, description: 'Query dormant leads matching criteria', color: 'text-blue-400', bgColor: 'bg-blue-500/10 border-blue-500/20' },
  { type: 'retrieve_context', label: 'Retrieve Context', icon: Search, description: 'Retrieve CRM history via RAG pipeline', color: 'text-purple-400', bgColor: 'bg-purple-500/10 border-purple-500/20' },
  { type: 'classify_lead', label: 'Classify Lead', icon: Brain, description: 'AI segment classification', color: 'text-pink-400', bgColor: 'bg-pink-500/10 border-pink-500/20' },
  { type: 'generate_message', label: 'Generate Message', icon: MessageSquare, description: 'Generate personalized outreach', color: 'text-green-400', bgColor: 'bg-green-500/10 border-green-500/20' },
  { type: 'human_approval', label: 'Human Approval', icon: UserCheck, description: 'Human review checkpoint', color: 'text-yellow-400', bgColor: 'bg-yellow-500/10 border-yellow-500/20' },
  { type: 'send_message', label: 'Send Message', icon: Send, description: 'Dispatch via email/SMS', color: 'text-blue-400', bgColor: 'bg-blue-500/10 border-blue-500/20' },
  { type: 'wait_for_reply', label: 'Wait for Reply', icon: Clock, description: 'Monitor inbound replies', color: 'text-orange-400', bgColor: 'bg-orange-500/10 border-orange-500/20' },
  { type: 'analyze_response', label: 'Analyze Response', icon: BarChart3, description: 'Classify reply sentiment', color: 'text-cyan-400', bgColor: 'bg-cyan-500/10 border-cyan-500/20' },
  { type: 'book_meeting', label: 'Book Meeting', icon: Calendar, description: 'Trigger meeting booking', color: 'text-emerald-400', bgColor: 'bg-emerald-500/10 border-emerald-500/20' },
  { type: 'escalate', label: 'Escalate', icon: AlertTriangle, description: 'Route to human SDR', color: 'text-red-400', bgColor: 'bg-red-500/10 border-red-500/20' },
]

interface WorkflowNode {
  id: string
  type: string
  x: number
  y: number
}

const defaultNodes: WorkflowNode[] = [
  { id: 'n1', type: 'fetch_leads', x: 260, y: 30 },
  { id: 'n2', type: 'retrieve_context', x: 260, y: 120 },
  { id: 'n3', type: 'classify_lead', x: 260, y: 210 },
  { id: 'n4', type: 'generate_message', x: 260, y: 300 },
  { id: 'n5', type: 'human_approval', x: 260, y: 390 },
  { id: 'n6', type: 'send_message', x: 260, y: 480 },
]

const connections = [
  ['n1', 'n2'], ['n2', 'n3'], ['n3', 'n4'], ['n4', 'n5'], ['n5', 'n6'],
]

const CHANNEL_OPTIONS = ['email', 'sms', 'whatsapp']

const CONFIG_OPTIONS = {
  generate_message: {
    fields: [
      { key: 'model', label: 'Model', type: 'select', options: ['GPT-4o', 'GPT-4o-mini', 'Claude Sonnet 4.6'] },
      { key: 'template', label: 'Prompt Template', type: 'select', options: ['pricing_objection_v3', 'timing_issue_v2', 'ghosted_v4', 'generic_reactivation_v1'] },
      { key: 'channel', label: 'Channel', type: 'select', options: CHANNEL_OPTIONS },
      { key: 'tone', label: 'Tone', type: 'select', options: ['Professional', 'Friendly', 'Direct', 'Empathetic'] },
      { key: 'maxRetries', label: 'Max Retries', type: 'input', defaultValue: '2' },
    ],
  },
  fetch_leads: {
    fields: [
      { key: 'minInactiveDays', label: 'Min Inactive Days', type: 'input', defaultValue: '30' },
      { key: 'maxInactiveDays', label: 'Max Inactive Days', type: 'input', defaultValue: '180' },
      { key: 'minDealValue', label: 'Min Deal Value ($)', type: 'input', defaultValue: '10000' },
      { key: 'limit', label: 'Max Leads', type: 'input', defaultValue: '100' },
    ],
  },
}

export default function CampaignBuilder() {
  const navigate = useNavigate()
  const [campaignName, setCampaignName] = useState('New Reactivation Campaign')
  const [channel, setChannel] = useState('email')
  const [nodes, setNodes] = useState<WorkflowNode[]>(defaultNodes)
  const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(defaultNodes[3])
  const [saving, setSaving] = useState(false)
  const [launching, setLaunching] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const NODE_WIDTH = 200
  const NODE_HEIGHT = 64

  function getNodeConfig(type: string) {
    return CONFIG_OPTIONS[type as keyof typeof CONFIG_OPTIONS] || null
  }

  async function handleSave() {
    setSaving(true)
    setError(null)
    try {
      await createCampaign({ name: campaignName, channel })
      navigate('/campaigns')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save campaign')
    } finally {
      setSaving(false)
    }
  }

  async function handleLaunch() {
    setLaunching(true)
    setError(null)
    try {
      const created = await createCampaign({ name: campaignName, channel })
      await launchCampaign(created.id)
      navigate('/campaigns')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to launch campaign')
    } finally {
      setLaunching(false)
    }
  }

  function handleConfigChange(key: string, value: string) {
    if (key === 'channel') setChannel(value.toLowerCase())
  }

  function getConfigValue(key: string, defaultValue?: string) {
    if (key === 'channel') return channel
    return defaultValue ?? ''
  }

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] -m-6">
      {/* Top Bar */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-border bg-card shrink-0">
        <Button variant="ghost" size="icon-sm" onClick={() => navigate('/campaigns')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <Input
          value={campaignName}
          onChange={e => setCampaignName(e.target.value)}
          className="max-w-xs h-8 text-sm font-medium bg-transparent border-transparent hover:border-border focus:border-ring"
        />
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground ml-2">
          <span className="bg-muted rounded px-1.5 py-0.5">{nodes.length} steps</span>
        </div>
        {error && (
          <span className="text-xs text-red-400 ml-2">{error}</span>
        )}
        <div className="ml-auto flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-1.5" onClick={handleSave} disabled={saving || launching}>
            {saving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
            {saving ? 'Saving…' : 'Save Draft'}
          </Button>
          <Button size="sm" className="gap-1.5 bg-green-600 hover:bg-green-700" onClick={handleLaunch} disabled={saving || launching}>
            {launching ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Rocket className="h-3.5 w-3.5" />}
            {launching ? 'Launching…' : 'Launch Campaign'}
          </Button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Palette */}
        <div className="w-64 border-r border-border bg-card flex flex-col shrink-0 overflow-y-auto scrollbar-thin">
          <div className="p-3 border-b border-border">
            <p className="text-xs font-semibold text-foreground">Node Palette</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">Drag nodes to the canvas to build your workflow</p>
          </div>

          {/* Campaign settings */}
          <div className="p-3 border-b border-border space-y-2">
            <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wide">Campaign Settings</p>
            <div>
              <label className="text-[10px] text-muted-foreground block mb-1">Channel</label>
              <select
                value={channel}
                onChange={e => setChannel(e.target.value)}
                className="w-full h-7 rounded-md border border-border bg-background text-xs text-foreground px-2 focus:outline-none focus:ring-1 focus:ring-ring"
              >
                {CHANNEL_OPTIONS.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            </div>
          </div>

          <div className="p-2 space-y-1.5">
            {nodeTypes.map(nt => (
              <div
                key={nt.type}
                className={cn("flex items-start gap-2.5 p-2 rounded-md border cursor-grab active:cursor-grabbing hover:brightness-110 transition-all", nt.bgColor)}
                draggable
                onDragStart={e => e.dataTransfer.setData('nodeType', nt.type)}
              >
                <nt.icon className={cn("h-4 w-4 mt-0.5 shrink-0", nt.color)} />
                <div className="min-w-0">
                  <p className="text-xs font-medium text-foreground">{nt.label}</p>
                  <p className="text-[10px] text-muted-foreground leading-tight">{nt.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Canvas */}
        <div
          className="flex-1 bg-background relative overflow-auto"
          style={{ backgroundImage: 'radial-gradient(circle, hsl(217 32% 17%) 1px, transparent 1px)', backgroundSize: '24px 24px' }}
          onDragOver={e => e.preventDefault()}
          onDrop={e => {
            const type = e.dataTransfer.getData('nodeType')
            if (!type) return
            const rect = e.currentTarget.getBoundingClientRect()
            const x = e.clientX - rect.left - NODE_WIDTH / 2
            const y = e.clientY - rect.top - NODE_HEIGHT / 2
            const newNode: WorkflowNode = { id: `n${Date.now()}`, type, x, y }
            setNodes(prev => [...prev, newNode])
          }}
        >
          <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ minWidth: 700, minHeight: 700 }}>
            {connections.map(([fromId, toId]) => {
              const from = nodes.find(n => n.id === fromId)
              const to = nodes.find(n => n.id === toId)
              if (!from || !to) return null
              const x1 = from.x + NODE_WIDTH / 2
              const y1 = from.y + NODE_HEIGHT
              const x2 = to.x + NODE_WIDTH / 2
              const y2 = to.y
              const my = (y1 + y2) / 2
              return (
                <g key={`${fromId}-${toId}`}>
                  <path
                    d={`M ${x1} ${y1} C ${x1} ${my} ${x2} ${my} ${x2} ${y2}`}
                    stroke="hsl(217 91% 60% / 0.4)"
                    strokeWidth={2}
                    fill="none"
                    strokeDasharray="5 3"
                  />
                  <polygon
                    points={`${x2},${y2} ${x2 - 5},${y2 - 8} ${x2 + 5},${y2 - 8}`}
                    fill="hsl(217 91% 60% / 0.6)"
                  />
                </g>
              )
            })}
          </svg>

          <div className="relative" style={{ minWidth: 700, minHeight: 700 }}>
            {nodes.map(node => {
              const nt = nodeTypes.find(t => t.type === node.type)
              if (!nt) return null
              const isSelected = selectedNode?.id === node.id
              return (
                <motion.div
                  key={node.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  style={{ position: 'absolute', left: node.x, top: node.y, width: NODE_WIDTH }}
                  className={cn(
                    "rounded-lg border p-3 cursor-pointer select-none shadow-lg transition-all",
                    nt.bgColor,
                    isSelected ? 'ring-2 ring-primary shadow-primary/20' : 'hover:ring-1 hover:ring-border'
                  )}
                  onClick={() => setSelectedNode(isSelected ? null : node)}
                >
                  <div className="flex items-center gap-2">
                    <nt.icon className={cn("h-4 w-4 shrink-0", nt.color)} />
                    <div className="min-w-0">
                      <p className="text-xs font-medium text-foreground truncate">{nt.label}</p>
                      <p className="text-[10px] text-muted-foreground truncate">{nt.description}</p>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>

          {/* Canvas label */}
          <div className="absolute bottom-4 left-4 text-[10px] text-muted-foreground/50">
            Drop nodes here to add them to the workflow
          </div>
        </div>

        {/* Right Config Panel */}
        <AnimatePresence>
          {selectedNode && (
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 300, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="border-l border-border bg-card flex flex-col shrink-0 overflow-hidden"
            >
              <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
                <div className="flex items-center gap-2">
                  <Settings2 className="h-4 w-4 text-muted-foreground" />
                  <p className="text-xs font-semibold text-foreground">Node Config</p>
                </div>
                <button onClick={() => setSelectedNode(null)} className="text-muted-foreground hover:text-foreground">
                  <X className="h-4 w-4" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-4">
                {(() => {
                  const nt = nodeTypes.find(t => t.type === selectedNode.type)
                  const cfg = getNodeConfig(selectedNode.type)
                  return (
                    <>
                      {nt && (
                        <div className={cn("flex items-center gap-2 p-2 rounded-md border", nt.bgColor)}>
                          <nt.icon className={cn("h-4 w-4", nt.color)} />
                          <span className="text-xs font-medium text-foreground">{nt.label}</span>
                        </div>
                      )}

                      {cfg ? (
                        <div className="space-y-3">
                          {cfg.fields.map(field => (
                            <div key={field.key}>
                              <label className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide block mb-1">
                                {field.label}
                              </label>
                              {field.type === 'select' ? (
                                <select
                                  className="w-full h-8 rounded-md border border-border bg-background text-xs text-foreground px-2 focus:outline-none focus:ring-1 focus:ring-ring"
                                  value={getConfigValue(field.key, 'options' in field ? field.options[0] : '')}
                                  onChange={e => handleConfigChange(field.key, e.target.value)}
                                >
                                  {'options' in field && field.options && field.options.map(o => (
                                    <option key={o} value={o}>{o}</option>
                                  ))}
                                </select>
                              ) : (
                                <Input defaultValue={'defaultValue' in field ? field.defaultValue : ''} className="h-8 text-xs" />
                              )}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="space-y-3">
                          <div>
                            <label className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide block mb-1">Node Name</label>
                            <Input defaultValue={selectedNode.type} className="h-8 text-xs" />
                          </div>
                          <div>
                            <label className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide block mb-1">Configuration</label>
                            <div className="text-xs text-muted-foreground bg-muted/30 rounded p-2">
                              No additional configuration required for this node type.
                            </div>
                          </div>
                        </div>
                      )}

                      <div className="pt-2 border-t border-border space-y-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="w-full text-xs text-red-400 border-red-500/30 hover:bg-red-500/10"
                          onClick={() => {
                            setNodes(prev => prev.filter(n => n.id !== selectedNode.id))
                            setSelectedNode(null)
                          }}
                        >
                          Remove Node
                        </Button>
                      </div>
                    </>
                  )
                })()}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
