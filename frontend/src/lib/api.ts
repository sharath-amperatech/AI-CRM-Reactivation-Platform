import type { Lead, CRMActivity, LeadSegment, LeadStatus } from '@/data/mockData'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const API_KEY = import.meta.env.VITE_API_KEY ?? ''

function authHeaders(): HeadersInit {
  return {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  }
}

interface ApiLead {
  id: string
  org_id: string
  hubspot_id: string | null
  name: string
  company: string
  email: string
  phone: string | null
  role: string | null
  segment: string
  status: string
  confidence: number
  deal_value: number
  inactive_days: number
  last_activity_at: string | null
  assigned_to_id: string | null
  industry: string | null
  company_size: string | null
  location: string | null
  source: string | null
  tags: string[]
  metadata: Record<string, unknown>
  crm_summary: string | null
  created_at: string
  updated_at: string
  enrollments?: Array<{
    id: string
    campaign_id: string
    campaign_name: string
    status: string
    enrolled_at: string
  }>
}

interface ApiActivity {
  id: string
  lead_id: string
  type: string
  occurred_at: string
  summary: string | null
  content: string | null
  sentiment: string | null
  author: string | null
  metadata: Record<string, unknown>
  created_at: string
}

interface ApiRAGChunk {
  source: string
  text: string
  score: number
  reranker: number
}

interface ApiLeadMessage {
  id: string
  channel: string
  subject: string | null
  body: string
  status: string
  sent_at: string | null
  created_at: string
  approval_id: string | null
  confidence: number
  ai_reasoning: string | null
  retrieved_chunks: ApiRAGChunk[]
  trace_id: string | null
  approval_status: string | null
}

interface ApiAuditLog {
  id: string
  action: string
  resource_type: string
  resource_id: string | null
  changes: Record<string, unknown>
  user_id: string | null
  user_name: string | null
  created_at: string
}

export interface LeadMessage {
  id: string
  channel: string
  subject: string | null
  body: string
  status: string
  sentAt: string | null
  createdAt: string
  approvalId: string | null
  confidence: number
  aiReasoning: string | null
  retrievedChunks: ApiRAGChunk[]
  traceId: string | null
  approvalStatus: string | null
}

export interface LeadAuditLog {
  id: string
  action: string
  resourceType: string
  resourceId: string | null
  changes: Record<string, unknown>
  userId: string | null
  userName: string | null
  createdAt: string
}

interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

function transformLead(raw: ApiLead): Lead {
  return {
    id: raw.id,
    name: raw.name,
    company: raw.company,
    email: raw.email,
    phone: raw.phone ?? '',
    role: raw.role ?? '',
    segment: raw.segment as LeadSegment,
    status: raw.status as LeadStatus,
    confidence: raw.confidence,
    dealValue: raw.deal_value,
    inactiveDays: raw.inactive_days,
    lastActivity: raw.last_activity_at ? raw.last_activity_at.split('T')[0] : '',
    assignedTo: (raw.metadata?.assigned_to_name as string) ?? 'Unassigned',
    campaigns: (raw.enrollments ?? []).map(e => e.campaign_name),
    tags: raw.tags ?? [],
    location: raw.location ?? '',
    industry: raw.industry ?? '',
    companySize: raw.company_size ?? '',
    source: raw.source ?? '',
    crmSummary: raw.crm_summary ?? null,
  }
}

function transformActivity(raw: ApiActivity): CRMActivity {
  return {
    id: raw.id,
    leadId: raw.lead_id,
    type: raw.type as CRMActivity['type'],
    date: raw.occurred_at.split('T')[0],
    summary: raw.summary ?? '',
    content: raw.content ?? '',
    sentiment: (raw.sentiment as CRMActivity['sentiment']) ?? 'neutral',
    author: raw.author ?? '',
  }
}

export async function fetchLeads(params?: {
  segment?: string
  status?: string
  search?: string
  page?: number
  page_size?: number
}): Promise<{ leads: Lead[]; total: number; pages: number }> {
  const query = new URLSearchParams()
  if (params?.segment) query.set('segment', params.segment)
  if (params?.status) query.set('status', params.status)
  if (params?.search) query.set('search', params.search)
  if (params?.page) query.set('page', String(params.page))
  if (params?.page_size) query.set('page_size', String(params.page_size))

  const res = await fetch(`${API_URL}/api/v1/leads?${query}`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch leads: ${res.status}`)
  const data: PaginatedResponse<ApiLead> = await res.json()
  return {
    leads: data.items.map(transformLead),
    total: data.total,
    pages: data.pages,
  }
}

export async function fetchLead(id: string): Promise<Lead> {
  const res = await fetch(`${API_URL}/api/v1/leads/${id}`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch lead: ${res.status}`)
  const data: ApiLead = await res.json()
  return transformLead(data)
}

export async function fetchLeadActivities(id: string): Promise<CRMActivity[]> {
  const res = await fetch(`${API_URL}/api/v1/leads/${id}/activities`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch activities: ${res.status}`)
  const data: ApiActivity[] = await res.json()
  return data.map(transformActivity)
}

function transformLeadMessage(raw: ApiLeadMessage): LeadMessage {
  return {
    id: raw.id,
    channel: raw.channel,
    subject: raw.subject,
    body: raw.body,
    status: raw.status,
    sentAt: raw.sent_at,
    createdAt: raw.created_at,
    approvalId: raw.approval_id,
    confidence: raw.confidence,
    aiReasoning: raw.ai_reasoning,
    retrievedChunks: raw.retrieved_chunks ?? [],
    traceId: raw.trace_id,
    approvalStatus: raw.approval_status,
  }
}

function transformAuditLog(raw: ApiAuditLog): LeadAuditLog {
  return {
    id: raw.id,
    action: raw.action,
    resourceType: raw.resource_type,
    resourceId: raw.resource_id,
    changes: raw.changes,
    userId: raw.user_id,
    userName: raw.user_name,
    createdAt: raw.created_at,
  }
}

export async function fetchLeadMessages(id: string): Promise<LeadMessage[]> {
  const res = await fetch(`${API_URL}/api/v1/leads/${id}/messages`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch messages: ${res.status}`)
  const data: ApiLeadMessage[] = await res.json()
  return data.map(transformLeadMessage)
}

export async function fetchLeadAuditLogs(id: string): Promise<LeadAuditLog[]> {
  const res = await fetch(`${API_URL}/api/v1/leads/${id}/audit`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch audit logs: ${res.status}`)
  const data: ApiAuditLog[] = await res.json()
  return data.map(transformAuditLog)
}

// ── Campaigns ─────────────────────────────────────────────────────────────────

export type CampaignStatus = 'active' | 'paused' | 'completed' | 'draft'

interface ApiCampaign {
  id: string
  org_id: string
  name: string
  description: string | null
  status: string
  channel: string
  segment: string | null
  ab_test: boolean
  enrolled_leads: number
  open_rate: number
  reply_rate: number
  meetings_booked: number
  converted_leads: number
  revenue_recovered: number
  total_steps: number
  steps_completed: number
  config: Record<string, unknown>
  started_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface Campaign {
  id: string
  name: string
  description: string | null
  status: CampaignStatus
  channel: string
  segment: string
  abTest: boolean
  enrolledLeads: number
  openRate: number
  replyRate: number
  meetingsBooked: number
  convertedLeads: number
  revenueRecovered: number
  totalSteps: number
  stepsCompleted: number
  startedAt: string | null
  completedAt: string | null
  createdAt: string
  updatedAt: string
}

function transformCampaign(raw: ApiCampaign): Campaign {
  return {
    id: raw.id,
    name: raw.name,
    description: raw.description,
    status: raw.status as CampaignStatus,
    channel: raw.channel,
    segment: raw.segment ?? '',
    abTest: raw.ab_test,
    enrolledLeads: raw.enrolled_leads,
    openRate: raw.open_rate,
    replyRate: raw.reply_rate,
    meetingsBooked: raw.meetings_booked,
    convertedLeads: raw.converted_leads,
    revenueRecovered: raw.revenue_recovered,
    totalSteps: raw.total_steps,
    stepsCompleted: raw.steps_completed,
    startedAt: raw.started_at,
    completedAt: raw.completed_at,
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
  }
}

interface ApiCampaignEnrollment {
  id: string
  lead_id: string
  enrolled_at: string
  status: string
  current_step: number
  lead: {
    id: string
    name: string
    company: string
    segment: string
    status: string
  }
}

export interface CampaignEnrollment {
  id: string
  leadId: string
  enrolledAt: string
  status: string
  currentStep: number
  lead: {
    id: string
    name: string
    company: string
    segment: string
    status: string
  }
}

interface ApiCampaignApproval {
  id: string
  lead_id: string
  campaign_id: string | null
  status: string
  confidence: number
  ai_reasoning: string | null
  lead_name: string | null
  company: string | null
  segment: string | null
  created_at: string
}

export interface CampaignApproval {
  id: string
  leadId: string
  status: string
  confidence: number
  aiReasoning: string | null
  leadName: string | null
  company: string | null
  segment: string | null
  createdAt: string
}

export async function fetchCampaigns(params?: {
  status?: string
  page?: number
  page_size?: number
}): Promise<{ campaigns: Campaign[]; total: number; pages: number }> {
  const query = new URLSearchParams()
  if (params?.status) query.set('status', params.status)
  if (params?.page) query.set('page', String(params.page))
  if (params?.page_size) query.set('page_size', String(params.page_size))

  const res = await fetch(`${API_URL}/api/v1/campaigns?${query}`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch campaigns: ${res.status}`)
  const data: PaginatedResponse<ApiCampaign> = await res.json()
  return {
    campaigns: data.items.map(transformCampaign),
    total: data.total,
    pages: data.pages,
  }
}

export async function fetchCampaign(id: string): Promise<Campaign> {
  const res = await fetch(`${API_URL}/api/v1/campaigns/${id}`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch campaign: ${res.status}`)
  const raw: ApiCampaign = await res.json()
  return transformCampaign(raw)
}

export async function createCampaign(data: {
  name: string
  description?: string
  channel: string
  segment?: string
  config?: Record<string, unknown>
}): Promise<Campaign> {
  const res = await fetch(`${API_URL}/api/v1/campaigns`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error(`Failed to create campaign: ${res.status}`)
  const raw: ApiCampaign = await res.json()
  return transformCampaign(raw)
}

export async function launchCampaign(id: string): Promise<Campaign> {
  const res = await fetch(`${API_URL}/api/v1/campaigns/${id}/launch`, {
    method: 'POST',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to launch campaign: ${res.status}`)
  const raw: ApiCampaign = await res.json()
  return transformCampaign(raw)
}

export async function pauseCampaign(id: string): Promise<Campaign> {
  const res = await fetch(`${API_URL}/api/v1/campaigns/${id}/pause`, {
    method: 'POST',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to pause campaign: ${res.status}`)
  const raw: ApiCampaign = await res.json()
  return transformCampaign(raw)
}

export async function resumeCampaign(id: string): Promise<Campaign> {
  const res = await fetch(`${API_URL}/api/v1/campaigns/${id}/resume`, {
    method: 'POST',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to resume campaign: ${res.status}`)
  const raw: ApiCampaign = await res.json()
  return transformCampaign(raw)
}

export async function fetchCampaignEnrollments(id: string): Promise<CampaignEnrollment[]> {
  const res = await fetch(`${API_URL}/api/v1/campaigns/${id}/enrollments`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch enrollments: ${res.status}`)
  const data: ApiCampaignEnrollment[] = await res.json()
  return data.map(e => ({
    id: e.id,
    leadId: e.lead_id,
    enrolledAt: e.enrolled_at,
    status: e.status,
    currentStep: e.current_step,
    lead: e.lead,
  }))
}

// ── Approvals ─────────────────────────────────────────────────────────────────

interface ApiApproval {
  id: string
  lead_id: string
  campaign_id: string | null
  status: string
  confidence: number
  crm_context: string | null
  ai_reasoning: string | null
  retrieved_chunks: Array<{ activity_id?: string; content?: string; activity_type?: string; occurred_at?: string; similarity_score?: number; rerank_score?: number | null; is_parent?: boolean } | string>
  trace_id: string | null
  approved_by_id: string | null
  approved_at: string | null
  edited_body: string | null
  rejection_reason: string | null
  created_at: string
  updated_at: string
  lead_name: string | null
  company: string | null
  segment: string | null
  deal_value: number | null
  campaign_name: string | null
  message_subject: string | null
  message_body: string | null
  channel: string | null
}

export interface Approval {
  id: string
  leadId: string
  leadName: string
  company: string
  segment: string
  confidence: number
  channel: string
  subject: string
  messageBody: string
  crmContext: string
  aiReasoning: string
  retrievedChunks: string[]
  traceId: string
  campaignId: string
  campaignName: string
  createdAt: string
  approvedBy: string | null
  status: 'pending' | 'approved' | 'rejected' | 'edited'
  dealValue: number
}

function transformApproval(raw: ApiApproval): Approval {
  const chunks = (raw.retrieved_chunks ?? []).map(c =>
    typeof c === 'string' ? c : (c.content ?? '')
  )
  const body = raw.status === 'edited' && raw.edited_body ? raw.edited_body : (raw.message_body ?? '')
  return {
    id: raw.id,
    leadId: raw.lead_id,
    leadName: raw.lead_name ?? '',
    company: raw.company ?? '',
    segment: raw.segment ?? '',
    confidence: raw.confidence,
    channel: raw.channel ?? 'email',
    subject: raw.message_subject ?? '',
    messageBody: body,
    crmContext: raw.crm_context ?? '',
    aiReasoning: raw.ai_reasoning ?? '',
    retrievedChunks: chunks,
    traceId: raw.trace_id ?? '',
    campaignId: raw.campaign_id ?? '',
    campaignName: raw.campaign_name ?? '',
    createdAt: raw.created_at,
    approvedBy: raw.approved_by_id,
    status: raw.status as Approval['status'],
    dealValue: raw.deal_value ?? 0,
  }
}

export async function fetchApprovals(params?: {
  page?: number
  page_size?: number
}): Promise<{ approvals: Approval[]; total: number; pages: number }> {
  const query = new URLSearchParams()
  if (params?.page) query.set('page', String(params.page))
  if (params?.page_size) query.set('page_size', String(params.page_size))

  const res = await fetch(`${API_URL}/api/v1/approvals?${query}`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch approvals: ${res.status}`)
  const data: PaginatedResponse<ApiApproval> = await res.json()
  return {
    approvals: data.items.map(transformApproval),
    total: data.total,
    pages: data.pages,
  }
}

export async function approveApproval(id: string): Promise<Approval> {
  const res = await fetch(`${API_URL}/api/v1/approvals/${id}/approve`, {
    method: 'POST',
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to approve: ${res.status}`)
  return transformApproval(await res.json())
}

export async function rejectApproval(id: string, reason?: string): Promise<Approval> {
  const res = await fetch(`${API_URL}/api/v1/approvals/${id}/reject`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ reason: reason ?? null }),
  })
  if (!res.ok) throw new Error(`Failed to reject: ${res.status}`)
  return transformApproval(await res.json())
}

export async function editAndApproveApproval(id: string, editedBody: string): Promise<Approval> {
  const res = await fetch(`${API_URL}/api/v1/approvals/${id}/edit`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ edited_body: editedBody }),
  })
  if (!res.ok) throw new Error(`Failed to edit and approve: ${res.status}`)
  return transformApproval(await res.json())
}

export async function bulkApproveHighConfidence(threshold = 0.85): Promise<string> {
  const res = await fetch(`${API_URL}/api/v1/approvals/bulk-approve`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ confidence_threshold: threshold }),
  })
  if (!res.ok) throw new Error(`Failed to bulk approve: ${res.status}`)
  const data: { message: string } = await res.json()
  return data.message
}

export async function fetchCampaignApprovals(id: string): Promise<CampaignApproval[]> {
  const res = await fetch(`${API_URL}/api/v1/campaigns/${id}/approvals`, {
    headers: authHeaders(),
  })
  if (!res.ok) throw new Error(`Failed to fetch approvals: ${res.status}`)
  const data: ApiCampaignApproval[] = await res.json()
  return data.map(a => ({
    id: a.id,
    leadId: a.lead_id,
    status: a.status,
    confidence: a.confidence,
    aiReasoning: a.ai_reasoning,
    leadName: a.lead_name,
    company: a.company,
    segment: a.segment,
    createdAt: a.created_at,
  }))
}
