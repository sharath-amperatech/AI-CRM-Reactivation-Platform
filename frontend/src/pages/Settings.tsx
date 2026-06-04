import { useState } from 'react'
import {
  CheckCircle, Link, Unlink, RefreshCw, Eye, EyeOff,
  Copy, Plus, Trash2, Edit3, Shield
} from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import DemoLabel from '@/components/shared/DemoLabel'
import { cn } from '@/lib/utils'

const integrations = [
  { id: 'hubspot', name: 'HubSpot CRM', status: 'connected', lastSync: '2026-05-25 07:12', color: 'text-orange-400', icon: '🟠' },
  { id: 'resend', name: 'Resend Email', status: 'configure', lastSync: null, color: 'text-blue-400', icon: '📧' },
  { id: 'twilio', name: 'Twilio SMS', status: 'configure', lastSync: null, color: 'text-red-400', icon: '📱' },
]

const promptTemplates = [
  { id: 'pt-001', segment: 'Pricing Objection', version: 'v3', lastUpdated: '2026-05-18', avgScore: 0.91 },
  { id: 'pt-002', segment: 'Timing Issue', version: 'v2', lastUpdated: '2026-05-15', avgScore: 0.89 },
  { id: 'pt-003', segment: 'Ghosted', version: 'v4', lastUpdated: '2026-05-12', avgScore: 0.84 },
  { id: 'pt-004', segment: 'Budget Constraints', version: 'v1', lastUpdated: '2026-05-10', avgScore: 0.86 },
  { id: 'pt-005', segment: 'Competitor Loss', version: 'v2', lastUpdated: '2026-05-08', avgScore: 0.88 },
]

const teamMembers = [
  { name: 'Sharath Kumar', email: 'sharath.kumar@amperatech.ai', role: 'Admin', avatar: 'S', since: '2026-01-10' },
  { name: 'Alex Rivera', email: 'alex.rivera@amperatech.ai', role: 'Sales Manager', avatar: 'A', since: '2026-02-14' },
  { name: 'Jordan Kim', email: 'jordan.kim@amperatech.ai', role: 'SDR', avatar: 'J', since: '2026-03-01' },
  { name: 'Sam Torres', email: 'sam.torres@amperatech.ai', role: 'SDR', avatar: 'T', since: '2026-03-15' },
]

const roleColors: Record<string, string> = {
  Admin: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  'Sales Manager': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  SDR: 'bg-green-500/20 text-green-400 border-green-500/30',
}

export default function Settings() {
  const [apiKeyVisible, setApiKeyVisible] = useState(false)
  const [semanticCache, setSemanticCache] = useState(true)
  const [temperature, setTemperature] = useState(0.7)
  const [syncing, setSyncing] = useState(false)
  const [copiedKey, setCopiedKey] = useState(false)

  const apiKey = 'riq_live_sk_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
  const maskedKey = 'riq_live_sk_••••••••••••••••••••••••••••'

  function handleSync() {
    setSyncing(true)
    setTimeout(() => setSyncing(false), 2500)
  }

  function handleCopyKey() {
    setCopiedKey(true)
    setTimeout(() => setCopiedKey(false), 2000)
  }

  return (
    <div className="space-y-4 max-w-4xl">
      <div>
        <h1 className="text-xl font-bold text-foreground">Settings</h1>
        <p className="text-xs text-muted-foreground mt-0.5">Configure integrations, AI models, prompts, and team access</p>
      </div>

      <Tabs defaultValue="integrations">
        <TabsList className="h-8">
          {['integrations', 'ai-config', 'prompts', 'team', 'billing', 'api-keys'].map(t => (
            <TabsTrigger key={t} value={t} className="text-xs capitalize">
              {t === 'ai-config' ? 'AI Config' : t === 'api-keys' ? 'API Keys' : t}
            </TabsTrigger>
          ))}
        </TabsList>

        {/* Integrations */}
        <TabsContent value="integrations" className="mt-4 space-y-4">
          {integrations.map(intg => (
            <Card key={intg.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{intg.icon}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-semibold text-foreground">{intg.name}</h3>
                        {intg.status === 'connected' ? (
                          <span className="inline-flex items-center gap-1 text-[10px] text-green-400 bg-green-500/10 border border-green-500/20 px-1.5 py-0.5 rounded">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                            Connected
                          </span>
                        ) : (
                          <span className="text-[10px] text-muted-foreground bg-muted/50 border border-border px-1.5 py-0.5 rounded">
                            Not configured
                          </span>
                        )}
                      </div>
                      {intg.lastSync && (
                        <p className="text-[10px] text-muted-foreground mt-0.5">Last sync: {intg.lastSync}</p>
                      )}
                      {intg.status !== 'connected' && (
                        <p className="text-[10px] text-muted-foreground mt-0.5">Connect your {intg.name} account to enable this integration.</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {intg.status === 'connected' ? (
                      <>
                        <Button size="sm" variant="outline" className="gap-1.5 h-7 text-xs" onClick={handleSync} disabled={syncing}>
                          {syncing ? <RefreshCw className="h-3 w-3 animate-spin" /> : <RefreshCw className="h-3 w-3" />}
                          {syncing ? 'Syncing...' : 'Re-sync'}
                        </Button>
                        <Button size="sm" variant="outline" className="gap-1.5 h-7 text-xs text-red-400 border-red-500/30 hover:bg-red-500/10">
                          <Unlink className="h-3 w-3" /> Disconnect
                        </Button>
                      </>
                    ) : (
                      <Button size="sm" className="gap-1.5 h-7 text-xs">
                        <Link className="h-3 w-3" /> Connect
                      </Button>
                    )}
                  </div>
                </div>
                {intg.id === 'hubspot' && (
                  <div className="mt-3 grid grid-cols-3 gap-3 pt-3 border-t border-border">
                    {[
                      { label: 'Contacts Synced', value: '2,847' },
                      { label: 'Activities Ingested', value: '14,291' },
                      { label: 'Last Sync Duration', value: '4.2s' },
                    ].map(stat => (
                      <div key={stat.label} className="text-center">
                        <p className="text-sm font-bold text-foreground">{stat.value}</p>
                        <p className="text-[10px] text-muted-foreground">{stat.label}</p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* AI Configuration */}
        <TabsContent value="ai-config" className="mt-4 space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">Model Configuration</CardTitle>
                <DemoLabel label="Sample Config" />
              </div>
            </CardHeader>
            <CardContent className="pt-0 space-y-4">
              <div>
                <Label className="text-xs text-muted-foreground mb-1 block">Primary Model</Label>
                <select className="w-full h-8 rounded-md border border-border bg-background text-xs text-foreground px-2 focus:outline-none focus:ring-1 focus:ring-ring">
                  <option>GPT-4o</option>
                  <option>GPT-4o-mini</option>
                  <option>Claude Sonnet 4.6</option>
                  <option>Llama 3.1 70B</option>
                </select>
              </div>
              <div>
                <Label className="text-xs text-muted-foreground mb-1 block">Fallback Chain</Label>
                <div className="flex items-center gap-2">
                  {['GPT-4o', '→', 'Claude Sonnet', '→', 'Llama 3 8B'].map((item, i) => (
                    item === '→'
                      ? <span key={i} className="text-muted-foreground text-xs">→</span>
                      : <span key={i} className="text-xs px-2 py-1 bg-muted border border-border rounded text-foreground font-medium">{item}</span>
                  ))}
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <Label className="text-xs text-muted-foreground">Temperature</Label>
                  <span className="text-xs font-medium text-foreground">{temperature}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={temperature}
                  onChange={e => setTemperature(parseFloat(e.target.value))}
                  className="w-full accent-primary"
                />
                <div className="flex justify-between text-[10px] text-muted-foreground mt-0.5">
                  <span>0 (Deterministic)</span>
                  <span>1 (Creative)</span>
                </div>
              </div>
              <div>
                <Label className="text-xs text-muted-foreground mb-1 block">Max Tokens</Label>
                <Input defaultValue="2048" className="h-8 text-xs max-w-xs" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Semantic Cache</CardTitle></CardHeader>
            <CardContent className="pt-0 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-foreground">Enable Semantic Caching</p>
                  <p className="text-[10px] text-muted-foreground mt-0.5">Reuse similar embeddings to reduce API costs</p>
                </div>
                <Switch checked={semanticCache} onCheckedChange={setSemanticCache} />
              </div>
              {semanticCache && (
                <div className="pl-4 border-l-2 border-primary/30 space-y-3">
                  <div>
                    <Label className="text-xs text-muted-foreground mb-1 block">Cache TTL (minutes)</Label>
                    <Input defaultValue="60" className="h-8 text-xs max-w-xs" />
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground mb-1 block">Similarity Threshold</Label>
                    <Input defaultValue="0.92" className="h-8 text-xs max-w-xs" />
                  </div>
                  <p className="text-[10px] text-green-400">Estimated monthly savings: ~$81 (62% cache hit rate)</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Prompt Templates */}
        <TabsContent value="prompts" className="mt-4 space-y-3">
          {promptTemplates.map(pt => (
            <Card key={pt.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-sm">📝</div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="text-xs font-medium text-foreground">{pt.segment}</p>
                        <Badge variant="outline" className="text-[10px] h-4 px-1">{pt.version}</Badge>
                        <span className="text-[10px] text-green-400 font-medium">{(pt.avgScore * 100).toFixed(0)}% avg score</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground mt-0.5">Last updated {pt.lastUpdated}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button size="sm" variant="ghost" className="h-7 text-xs gap-1">
                      <Eye className="h-3 w-3" /> Preview
                    </Button>
                    <Button size="sm" variant="outline" className="h-7 text-xs gap-1">
                      <Edit3 className="h-3 w-3" /> Edit
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
          <Button variant="outline" size="sm" className="gap-1.5 w-full">
            <Plus className="h-3.5 w-3.5" /> Add Template
          </Button>
        </TabsContent>

        {/* Team */}
        <TabsContent value="team" className="mt-4 space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-muted-foreground">{teamMembers.length} members</p>
            <Button size="sm" className="gap-1.5">
              <Plus className="h-3.5 w-3.5" /> Invite Member
            </Button>
          </div>
          <Card>
            <div className="divide-y divide-border">
              {teamMembers.map(member => (
                <div key={member.email} className="flex items-center justify-between px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-bold text-primary">
                      {member.avatar}
                    </div>
                    <div>
                      <p className="text-xs font-medium text-foreground">{member.name}</p>
                      <p className="text-[10px] text-muted-foreground">{member.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-[10px] text-muted-foreground">Since {member.since}</span>
                    <span className={cn("inline-flex items-center px-2 py-0.5 rounded-md border text-[10px] font-medium", roleColors[member.role])}>
                      {member.role}
                    </span>
                    <Button size="sm" variant="ghost" className="h-7 text-xs gap-1 text-muted-foreground">
                      <Edit3 className="h-3 w-3" />
                    </Button>
                    {member.email !== 'sharath.kumar@amperatech.ai' && (
                      <Button size="sm" variant="ghost" className="h-7 text-xs gap-1 text-red-400 hover:bg-red-500/10">
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        {/* Billing */}
        <TabsContent value="billing" className="mt-4 space-y-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-sm font-bold text-foreground">Pro Plan</h3>
                    <Badge variant="success" className="text-[10px]">Active</Badge>
                  </div>
                  <p className="text-2xl font-bold text-foreground mt-1">$299<span className="text-sm font-normal text-muted-foreground">/month</span></p>
                  <p className="text-xs text-muted-foreground mt-0.5">Billed monthly · Next billing: 2026-06-01</p>
                </div>
                <Button size="sm" className="gap-1.5">Upgrade to Enterprise</Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Usage This Month</CardTitle></CardHeader>
            <CardContent className="pt-0 space-y-3">
              {[
                { label: 'Leads Processed', value: 847, limit: 1000 },
                { label: 'AI Generations', value: 1847, limit: 5000 },
                { label: 'API Calls', value: 12481, limit: 50000 },
              ].map(u => (
                <div key={u.label}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted-foreground">{u.label}</span>
                    <span className="text-foreground font-medium">{u.value.toLocaleString()} / {u.limit.toLocaleString()}</span>
                  </div>
                  <div className="h-1.5 bg-muted rounded-full">
                    <div className={cn("h-1.5 rounded-full", u.value / u.limit > 0.8 ? 'bg-yellow-500' : 'bg-primary')} style={{ width: `${Math.round(u.value / u.limit * 100)}%` }} />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Keys */}
        <TabsContent value="api-keys" className="mt-4 space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-primary" />
                <CardTitle className="text-sm">API Key</CardTitle>
              </div>
              <CardDescription>Use this key to authenticate requests to the ReactivIQ API.</CardDescription>
            </CardHeader>
            <CardContent className="pt-0 space-y-3">
              <div className="flex items-center gap-2">
                <Input
                  readOnly
                  value={apiKeyVisible ? apiKey : maskedKey}
                  className="h-8 text-xs font-mono flex-1"
                />
                <Button size="icon-sm" variant="outline" onClick={() => setApiKeyVisible(!apiKeyVisible)}>
                  {apiKeyVisible ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                </Button>
                <Button size="icon-sm" variant="outline" onClick={handleCopyKey}>
                  <Copy className="h-3.5 w-3.5" />
                </Button>
                {copiedKey && <span className="text-[10px] text-green-400">Copied!</span>}
              </div>
              <div className="flex items-center gap-2">
                <Button size="sm" variant="outline" className="gap-1.5 text-xs h-7">
                  <RefreshCw className="h-3 w-3" /> Regenerate Key
                </Button>
                <p className="text-[10px] text-muted-foreground">Last used: 2026-05-25 07:12 UTC</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Webhook URL</CardTitle>
              <CardDescription>ReactivIQ sends events to this URL.</CardDescription>
            </CardHeader>
            <CardContent className="pt-0 space-y-3">
              <div className="flex items-center gap-2">
                <Input
                  defaultValue="https://api.amperatech.ai/webhooks/reactiviq"
                  className="h-8 text-xs font-mono flex-1"
                />
                <Button size="sm" variant="outline" className="text-xs h-8">Save</Button>
              </div>
              <div className="space-y-1">
                <p className="text-[10px] font-medium text-muted-foreground">Events sent:</p>
                <div className="flex flex-wrap gap-1.5">
                  {['approval.created', 'approval.approved', 'approval.rejected', 'campaign.completed', 'lead.reactivated'].map(e => (
                    <Badge key={e} variant="secondary" className="text-[10px]">{e}</Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
