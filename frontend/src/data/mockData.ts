export type LeadSegment = 'pricing_objection' | 'timing_issue' | 'competitor_loss' | 'ghosted' | 'no_decision_maker' | 'budget_constraints' | 'feature_gap' | 'unknown'
export type LeadStatus = 'dormant' | 'active' | 'reactivated' | 'lost' | 'meeting_booked'
export type CampaignStatus = 'draft' | 'active' | 'paused' | 'completed'
export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'edited'
export type MessageChannel = 'email' | 'sms' | 'whatsapp'

export interface Lead {
  id: string
  name: string
  company: string
  email: string
  phone: string
  role: string
  segment: LeadSegment
  status: LeadStatus
  confidence: number
  dealValue: number
  inactiveDays: number
  lastActivity: string
  assignedTo: string
  campaigns: string[]
  tags: string[]
  location: string
  industry: string
  companySize: string
  source: string
  crmSummary: string | null
}

export interface CRMActivity {
  id: string
  leadId: string
  type: 'email' | 'call' | 'meeting' | 'note' | 'deal_update'
  date: string
  summary: string
  content: string
  sentiment: 'positive' | 'neutral' | 'negative'
  author: string
}

export interface Campaign {
  id: string
  name: string
  status: CampaignStatus
  segment: LeadSegment | 'all'
  enrolledLeads: number
  openRate: number
  replyRate: number
  meetingsBooked: number
  convertedLeads: number
  revenueRecovered: number
  createdAt: string
  startedAt: string
  stepsCompleted: number
  totalSteps: number
  channel: MessageChannel
  abTest: boolean
}

export interface ApprovalItem {
  id: string
  leadId: string
  leadName: string
  company: string
  segment: LeadSegment
  confidence: number
  channel: MessageChannel
  subject: string
  messageBody: string
  crmContext: string
  aiReasoning: string
  retrievedChunks: string[]
  traceId: string
  campaignId: string
  campaignName: string
  createdAt: string
  approvedBy?: string
  status: ApprovalStatus
  dealValue: number
}

export interface WorkflowNode {
  id: string
  type: string
  label: string
  description: string
  x: number
  y: number
  config: Record<string, unknown>
}

export interface AnalyticsDataPoint {
  date: string
  revenue: number
  leads: number
  meetings: number
  emails: number
}

export interface RAGASMetric {
  date: string
  faithfulness: number
  answerRelevancy: number
  contextRecall: number
  contextPrecision: number
}

// ===== MOCK LEADS =====
export const mockLeads: Lead[] = [
  {
    id: 'lead-001',
    name: 'Sarah Chen',
    company: 'TechFlow Solutions',
    email: 'sarah.chen@techflow.io',
    phone: '+1 (415) 555-0182',
    role: 'VP of Engineering',
    segment: 'pricing_objection',
    status: 'dormant',
    confidence: 0.91,
    dealValue: 48000,
    inactiveDays: 67,
    lastActivity: '2026-03-19',
    assignedTo: 'Alex Rivera',
    campaigns: ['campaign-001'],
    tags: ['enterprise', 'high-value', 'technical'],
    location: 'San Francisco, CA',
    industry: 'SaaS',
    companySize: '200-500',
    source: 'HubSpot',
    crmSummary: null,
  },
  {
    id: 'lead-002',
    name: 'Marcus Williams',
    company: 'GrowthBase Inc',
    email: 'marcus@growthbase.com',
    phone: '+1 (312) 555-0241',
    role: 'CEO',
    segment: 'timing_issue',
    status: 'dormant',
    confidence: 0.84,
    dealValue: 32000,
    inactiveDays: 45,
    lastActivity: '2026-04-10',
    assignedTo: 'Jordan Kim',
    campaigns: ['campaign-002'],
    tags: ['startup', 'high-intent'],
    location: 'Chicago, IL',
    industry: 'Marketing Tech',
    companySize: '50-200',
    source: 'HubSpot',
    crmSummary: null,
  },
  {
    id: 'lead-003',
    name: 'Priya Patel',
    company: 'Meridian Analytics',
    email: 'priya.patel@meridian.ai',
    phone: '+1 (212) 555-0309',
    role: 'Head of RevOps',
    segment: 'competitor_loss',
    status: 'dormant',
    confidence: 0.78,
    dealValue: 75000,
    inactiveDays: 112,
    lastActivity: '2026-02-03',
    assignedTo: 'Alex Rivera',
    campaigns: [],
    tags: ['enterprise', 'revops', 'high-value'],
    location: 'New York, NY',
    industry: 'Analytics',
    companySize: '500-2000',
    source: 'HubSpot',
    crmSummary: null,
  },
  {
    id: 'lead-004',
    name: 'David Okafor',
    company: 'Nexus Capital Partners',
    email: 'd.okafor@nexuscap.com',
    phone: '+1 (310) 555-0127',
    role: 'Managing Director',
    segment: 'ghosted',
    status: 'dormant',
    confidence: 0.65,
    dealValue: 120000,
    inactiveDays: 89,
    lastActivity: '2026-02-25',
    assignedTo: 'Jordan Kim',
    campaigns: ['campaign-001'],
    tags: ['financial', 'enterprise', 'warm'],
    location: 'Los Angeles, CA',
    industry: 'Finance',
    companySize: '50-200',
    source: 'HubSpot',
    crmSummary: null,
  },
  {
    id: 'lead-005',
    name: 'Elena Rodriguez',
    company: 'CloudFirst Systems',
    email: 'elena.r@cloudfirst.com',
    phone: '+1 (512) 555-0398',
    role: 'CTO',
    segment: 'budget_constraints',
    status: 'dormant',
    confidence: 0.88,
    dealValue: 28000,
    inactiveDays: 53,
    lastActivity: '2026-04-02',
    assignedTo: 'Sam Torres',
    campaigns: ['campaign-003'],
    tags: ['cloud', 'technical', 'mid-market'],
    location: 'Austin, TX',
    industry: 'Cloud Infrastructure',
    companySize: '100-500',
    source: 'HubSpot',
    crmSummary: null,
  },
  {
    id: 'lead-006',
    name: 'James Liu',
    company: 'Quantum Retail Co.',
    email: 'j.liu@quantumretail.com',
    phone: '+1 (617) 555-0215',
    role: 'Director of Technology',
    segment: 'feature_gap',
    status: 'reactivated',
    confidence: 0.72,
    dealValue: 55000,
    inactiveDays: 30,
    lastActivity: '2026-04-25',
    assignedTo: 'Alex Rivera',
    campaigns: ['campaign-002', 'campaign-004'],
    tags: ['retail', 'integration-heavy'],
    location: 'Boston, MA',
    industry: 'Retail Tech',
    companySize: '200-500',
    source: 'HubSpot',
    crmSummary: null,
  },
  {
    id: 'lead-007',
    name: 'Amara Nwosu',
    company: 'Pinnacle Health AI',
    email: 'amara@pinnaclehealth.ai',
    phone: '+1 (415) 555-0467',
    role: 'VP of Product',
    segment: 'timing_issue',
    status: 'meeting_booked',
    confidence: 0.95,
    dealValue: 92000,
    inactiveDays: 0,
    lastActivity: '2026-05-23',
    assignedTo: 'Jordan Kim',
    campaigns: ['campaign-001'],
    tags: ['health-tech', 'high-value', 'hot'],
    location: 'San Francisco, CA',
    industry: 'Health Tech',
    companySize: '100-500',
    source: 'HubSpot',
    crmSummary: null,
  },
  {
    id: 'lead-008',
    name: 'Tyler Brennan',
    company: 'Forge Manufacturing',
    email: 'tyler.brennan@forge-mfg.com',
    phone: '+1 (216) 555-0334',
    role: 'Operations Director',
    segment: 'no_decision_maker',
    status: 'dormant',
    confidence: 0.58,
    dealValue: 38000,
    inactiveDays: 78,
    lastActivity: '2026-03-07',
    assignedTo: 'Sam Torres',
    campaigns: [],
    tags: ['manufacturing', 'needs-champion'],
    location: 'Cleveland, OH',
    industry: 'Manufacturing',
    companySize: '500-2000',
    source: 'HubSpot',
    crmSummary: null,
  },
  {
    id: 'lead-009',
    name: 'Natasha Ivanova',
    company: 'DataSphere Analytics',
    email: 'n.ivanova@datasphere.io',
    phone: '+1 (206) 555-0289',
    role: 'Chief Data Officer',
    segment: 'pricing_objection',
    status: 'dormant',
    confidence: 0.86,
    dealValue: 64000,
    inactiveDays: 42,
    lastActivity: '2026-04-13',
    assignedTo: 'Alex Rivera',
    campaigns: ['campaign-004'],
    tags: ['data', 'enterprise', 'evaluating'],
    location: 'Seattle, WA',
    industry: 'Data Analytics',
    companySize: '200-500',
    source: 'HubSpot',
    crmSummary: null,
  },
  {
    id: 'lead-010',
    name: 'Carlos Mendez',
    company: 'Vantage Logistics',
    email: 'c.mendez@vantagelogistics.com',
    phone: '+1 (713) 555-0156',
    role: 'COO',
    segment: 'ghosted',
    status: 'dormant',
    confidence: 0.61,
    dealValue: 85000,
    inactiveDays: 134,
    lastActivity: '2026-01-11',
    assignedTo: 'Jordan Kim',
    campaigns: [],
    tags: ['logistics', 'enterprise', 'cold'],
    location: 'Houston, TX',
    industry: 'Logistics',
    companySize: '500-2000',
    source: 'HubSpot',
    crmSummary: null,
  },
]

export const mockCRMActivities: CRMActivity[] = [
  {
    id: 'act-001',
    leadId: 'lead-001',
    type: 'email',
    date: '2026-03-19',
    summary: 'Pricing concerns raised — wants 30% discount for annual plan',
    content: 'Hi Alex, I wanted to follow up on our demo call last week. The platform looks great for our engineering team. However, the pricing is significantly above our Q2 budget. Is there any flexibility, particularly for an annual commitment? We are evaluating 2-3 other vendors. Please let me know by end of week. — Sarah',
    sentiment: 'negative',
    author: 'Sarah Chen',
  },
  {
    id: 'act-002',
    leadId: 'lead-001',
    type: 'meeting',
    date: '2026-03-12',
    summary: 'Product demo — strong interest in AI features, budget concerns surfaced',
    content: 'Full platform demo conducted. Sarah and her team (3 engineers) attended. Very positive reception to the workflow builder and AI observability features. Budget discussion at end: mentioned $40K budget cap vs $55K quoted. Requested a revised proposal.',
    sentiment: 'positive',
    author: 'Alex Rivera',
  },
  {
    id: 'act-003',
    leadId: 'lead-001',
    type: 'call',
    date: '2026-03-05',
    summary: 'Discovery call — confirmed budget, timeline, and technical requirements',
    content: 'Discovery call notes: TechFlow is evaluating AI workflow tools for their RevOps team. 200-person company, scaling. Budget range $40-60K annually. Timeline: Q2 2026 decision. Key requirements: API integrations, audit logs, enterprise SSO.',
    sentiment: 'positive',
    author: 'Alex Rivera',
  },
  {
    id: 'act-004',
    leadId: 'lead-001',
    type: 'note',
    date: '2026-02-28',
    summary: 'Inbound interest — requested pricing page',
    content: 'Sarah submitted contact form requesting pricing. Assigned to Alex. Source: LinkedIn campaign.',
    sentiment: 'neutral',
    author: 'System',
  },
  {
    id: 'act-005',
    leadId: 'lead-002',
    type: 'email',
    date: '2026-04-10',
    summary: 'Replied saying not the right time — Q3 budget cycle',
    content: 'Jordan, thanks for following up. We are very interested in ReactivIQ but our Q2 budget is fully committed. We would like to revisit in Q3 when our new budget cycle begins (July). Please reach out then. — Marcus',
    sentiment: 'neutral',
    author: 'Marcus Williams',
  },
  {
    id: 'act-006',
    leadId: 'lead-002',
    type: 'meeting',
    date: '2026-03-28',
    summary: 'Executive demo — strong interest, timing mismatch identified',
    content: 'Marcus attended solo. Showed deep interest in the campaign builder and approval workflows. Has a team of 5 SDRs who spend 60% of time on manual follow-up. Clear pain point match. Budget availability issue: Q2 headcount freeze. Q3 likely.',
    sentiment: 'positive',
    author: 'Jordan Kim',
  },
]

export const mockCampaigns: Campaign[] = [
  {
    id: 'campaign-001',
    name: 'Q2 Pricing Objection Revival',
    status: 'active',
    segment: 'pricing_objection',
    enrolledLeads: 47,
    openRate: 68.4,
    replyRate: 22.1,
    meetingsBooked: 8,
    convertedLeads: 3,
    revenueRecovered: 184000,
    createdAt: '2026-04-15',
    startedAt: '2026-04-20',
    stepsCompleted: 3,
    totalSteps: 5,
    channel: 'email',
    abTest: true,
  },
  {
    id: 'campaign-002',
    name: 'Timing Issue — Q3 Re-Engage',
    status: 'active',
    segment: 'timing_issue',
    enrolledLeads: 62,
    openRate: 71.2,
    replyRate: 18.5,
    meetingsBooked: 11,
    convertedLeads: 4,
    revenueRecovered: 248000,
    createdAt: '2026-04-22',
    startedAt: '2026-04-28',
    stepsCompleted: 2,
    totalSteps: 4,
    channel: 'email',
    abTest: false,
  },
  {
    id: 'campaign-003',
    name: 'Ghost Recovery — High Value',
    status: 'active',
    segment: 'ghosted',
    enrolledLeads: 31,
    openRate: 52.3,
    replyRate: 9.7,
    meetingsBooked: 3,
    convertedLeads: 1,
    revenueRecovered: 92000,
    createdAt: '2026-05-01',
    startedAt: '2026-05-08',
    stepsCompleted: 1,
    totalSteps: 6,
    channel: 'email',
    abTest: true,
  },
  {
    id: 'campaign-004',
    name: 'Budget Unlock — Annual Offer',
    status: 'paused',
    segment: 'budget_constraints',
    enrolledLeads: 28,
    openRate: 61.5,
    replyRate: 14.3,
    meetingsBooked: 5,
    convertedLeads: 2,
    revenueRecovered: 76000,
    createdAt: '2026-03-10',
    startedAt: '2026-03-15',
    stepsCompleted: 4,
    totalSteps: 5,
    channel: 'email',
    abTest: false,
  },
  {
    id: 'campaign-005',
    name: 'Competitor Win-Back Campaign',
    status: 'completed',
    segment: 'competitor_loss',
    enrolledLeads: 19,
    openRate: 79.3,
    replyRate: 31.5,
    meetingsBooked: 6,
    convertedLeads: 2,
    revenueRecovered: 154000,
    createdAt: '2026-02-01',
    startedAt: '2026-02-10',
    stepsCompleted: 5,
    totalSteps: 5,
    channel: 'email',
    abTest: true,
  },
]

export const mockApprovals: ApprovalItem[] = [
  {
    id: 'approval-001',
    leadId: 'lead-001',
    leadName: 'Sarah Chen',
    company: 'TechFlow Solutions',
    segment: 'pricing_objection',
    confidence: 0.91,
    channel: 'email',
    subject: 'A custom proposal for TechFlow — because great engineering teams deserve better pricing',
    messageBody: `Hi Sarah,

I hope this email finds you well. I've been thinking about our conversation back in March — specifically around the pricing concerns you raised for TechFlow's engineering team.

I went back to our records and pulled up the context from our last few touchpoints: your team's excitement about the workflow builder, the demo feedback from your three engineers, and the $40K budget ceiling you mentioned.

I'd love to work within that. Here's what I can offer:

**Custom Annual Plan — $38,400/year**
- Full platform access for up to 15 seats
- Priority onboarding + dedicated CSM
- Custom SLA terms
- 90-day satisfaction guarantee

Given that TechFlow is evaluating other vendors and your Q2 timeline is approaching, I wanted to get this in front of you now rather than later.

Would a 20-minute call this week make sense? I can walk you through the updated proposal and answer any lingering questions.

Best,
Alex Rivera
Senior Account Executive`,
    crmContext: 'Sarah raised pricing concerns in March 2026, referencing a $40K budget cap vs $55K quote. Team of 3 engineers attended demo with positive feedback on workflow builder and AI observability.',
    aiReasoning: 'Lead classified as pricing_objection (confidence: 0.91). Retrieved 4 CRM chunks including: March pricing email, demo meeting notes, discovery call transcript. Message personalized with specific budget figure ($40K), team composition (3 engineers), and product interests (workflow builder). Tone: professional with urgency indicator. Custom discount included within acceptable range (12% below list).',
    retrievedChunks: [
      'March 19 email: "the pricing is significantly above our Q2 budget... $40K budget cap"',
      'March 12 demo notes: "Sarah and her team (3 engineers)... Very positive reception to workflow builder"',
      'March 5 discovery: "Budget range $40-60K annually. Timeline: Q2 2026 decision"',
      'Feb 28 note: "Inbound interest — requested pricing page. Source: LinkedIn campaign"',
    ],
    traceId: 'trace-a1b2c3d4',
    campaignId: 'campaign-001',
    campaignName: 'Q2 Pricing Objection Revival',
    createdAt: '2026-05-25T08:32:00Z',
    status: 'pending',
    dealValue: 48000,
  },
  {
    id: 'approval-002',
    leadId: 'lead-002',
    leadName: 'Marcus Williams',
    company: 'GrowthBase Inc',
    segment: 'timing_issue',
    confidence: 0.84,
    channel: 'email',
    subject: 'Q3 is around the corner — your SDRs are still doing this manually',
    messageBody: `Hi Marcus,

Back in April, you mentioned GrowthBase would be ready to revisit ReactivIQ in Q3 as your new budget cycle kicks in. Q3 starts in just over 5 weeks — I wanted to reach out ahead of that window.

A quick reminder of what your team stands to gain:
- Your 5 SDRs are spending ~60% of their time on manual follow-up (our conversation in March)
- ReactivIQ automates the full reactivation workflow end-to-end
- Average customer recovers $180K+ in dormant pipeline within 90 days

If you're planning to include this in your Q3 budget, I'd love to get you set up with a dedicated proof-of-concept before July. That way you start Q3 running, not evaluating.

15 minutes this week?

Best,
Jordan Kim`,
    crmContext: 'Marcus said in April email: Q2 budget committed, revisit in Q3 (July). Demo in March showed strong interest — 5 SDR team, 60% time on manual follow-up.',
    aiReasoning: 'Lead segment: timing_issue (confidence: 0.84). Key retrieval: Q3 timing commitment, SDR team size, manual workflow pain. Message anchors on Q3 timeline to create urgency without pressure. Included ROI reference ($180K average) to build business case for Q3 budget allocation.',
    retrievedChunks: [
      'April 10 email: "Q2 budget is fully committed... revisit in Q3 when our new budget cycle begins (July)"',
      'March 28 demo: "team of 5 SDRs who spend 60% of time on manual follow-up. Clear pain point match"',
    ],
    traceId: 'trace-e5f6g7h8',
    campaignId: 'campaign-002',
    campaignName: 'Timing Issue — Q3 Re-Engage',
    createdAt: '2026-05-25T09:14:00Z',
    status: 'pending',
    dealValue: 32000,
  },
  {
    id: 'approval-003',
    leadId: 'lead-005',
    leadName: 'Elena Rodriguez',
    company: 'CloudFirst Systems',
    segment: 'budget_constraints',
    confidence: 0.88,
    channel: 'email',
    subject: 'CloudFirst + ReactivIQ — starter plan that fits your Q2 runway',
    messageBody: `Hi Elena,

Following up on our conversation from April. You mentioned CloudFirst is in the middle of a lean quarter before your Series B closes. I completely understand — timing matters.

That's why I wanted to reach out with our new Starter Plan, which was specifically designed for high-growth companies in exactly your position:

**ReactivIQ Starter — $1,800/month**
- 5 user seats
- Up to 500 dormant leads per month
- Full AI campaign automation
- Human-in-the-loop approvals
- Cancel anytime

You get the full platform at a scale that fits today's runway, and you can upgrade the moment your Series B lands.

Happy to hop on a call this week to walk you through it. Would Thursday or Friday work?

Sam Torres`,
    crmContext: 'Elena mentioned budget constraints in April — CloudFirst in lean quarter before Series B. CTO with technical background, evaluating cloud infrastructure tools.',
    aiReasoning: 'Segment: budget_constraints (confidence: 0.88). Budget concern: pre-Series B lean quarter. Solution: tiered starter plan at lower price point with upgrade path. Retrieved chunks confirm CTO-level decision authority and specific funding stage. Message avoids hard sell, offers flexibility.',
    retrievedChunks: [
      'April 2 call: "in a lean quarter before our Series B closes... budget is constrained until funding comes through"',
      'March activity: "CTO level, decision authority confirmed, evaluating 3 vendors"',
    ],
    traceId: 'trace-i9j0k1l2',
    campaignId: 'campaign-004',
    campaignName: 'Budget Unlock — Annual Offer',
    createdAt: '2026-05-24T16:45:00Z',
    status: 'pending',
    dealValue: 28000,
  },
  {
    id: 'approval-004',
    leadId: 'lead-009',
    leadName: 'Natasha Ivanova',
    company: 'DataSphere Analytics',
    segment: 'pricing_objection',
    confidence: 0.86,
    channel: 'email',
    subject: 'DataSphere — the ROI case you asked for',
    messageBody: `Hi Natasha,

You asked during our call for a clearer ROI breakdown before committing to ReactivIQ. Here it is.

DataSphere Analytics context:
- ~200 dormant leads in HubSpot (based on your team's estimate)
- Average deal value: $64K
- Industry reactivation rate with ReactivIQ: 8-12%

Conservative ROI projection (6 months):
- Leads reactivated: 16-24
- Revenue recovered: $1.02M–$1.54M
- ReactivIQ cost: $96K annually
- Net ROI: **10x–16x**

I've also attached a case study from a comparable analytics firm (100-person team, similar HubSpot setup) that recovered $2.1M in year one.

Ready to do a 30-minute ROI deep-dive call? I can also connect you with their CDO directly if that would help.

Alex Rivera`,
    crmContext: 'Natasha asked for ROI data in April call. DataSphere has ~200 dormant leads estimated. Pricing objection driven by needing clearer business case, not absolute budget constraints.',
    aiReasoning: 'Segment: pricing_objection — but nuanced as data-driven objection, not affordability. Retrieved chunks: ROI request, lead count estimate, deal value data. Message delivers specific ROI calculation using their own numbers. High confidence due to clear ask and specific data points available.',
    retrievedChunks: [
      "April 13 call: \"need a clearer ROI breakdown... have about 200 dormant leads we've been ignoring\"",
      'HubSpot data: avg deal value $64K, CDO role confirmed',
    ],
    traceId: 'trace-m3n4o5p6',
    campaignId: 'campaign-004',
    campaignName: 'Budget Unlock — Annual Offer',
    createdAt: '2026-05-24T11:20:00Z',
    status: 'approved',
    approvedBy: 'Alex Rivera',
    dealValue: 64000,
  },
]

export const mockAnalyticsData: AnalyticsDataPoint[] = [
  { date: '2026-01-01', revenue: 42000, leads: 12, meetings: 4, emails: 847 },
  { date: '2026-01-15', revenue: 58000, leads: 18, meetings: 6, emails: 1203 },
  { date: '2026-02-01', revenue: 91000, leads: 24, meetings: 9, emails: 1567 },
  { date: '2026-02-15', revenue: 124000, leads: 31, meetings: 12, emails: 2108 },
  { date: '2026-03-01', revenue: 167000, leads: 38, meetings: 15, emails: 2543 },
  { date: '2026-03-15', revenue: 198000, leads: 44, meetings: 18, emails: 2987 },
  { date: '2026-04-01', revenue: 241000, leads: 52, meetings: 22, emails: 3421 },
  { date: '2026-04-15', revenue: 287000, leads: 61, meetings: 27, emails: 3876 },
  { date: '2026-05-01', revenue: 312000, leads: 68, meetings: 31, emails: 4234 },
  { date: '2026-05-15', revenue: 347000, leads: 74, meetings: 35, emails: 4598 },
]

export const mockRAGASMetrics: RAGASMetric[] = [
  { date: '2026-04-01', faithfulness: 0.82, answerRelevancy: 0.79, contextRecall: 0.71, contextPrecision: 0.76 },
  { date: '2026-04-08', faithfulness: 0.84, answerRelevancy: 0.81, contextRecall: 0.73, contextPrecision: 0.78 },
  { date: '2026-04-15', faithfulness: 0.87, answerRelevancy: 0.83, contextRecall: 0.76, contextPrecision: 0.80 },
  { date: '2026-04-22', faithfulness: 0.85, answerRelevancy: 0.86, contextRecall: 0.79, contextPrecision: 0.83 },
  { date: '2026-04-29', faithfulness: 0.89, answerRelevancy: 0.88, contextRecall: 0.81, contextPrecision: 0.85 },
  { date: '2026-05-06', faithfulness: 0.91, answerRelevancy: 0.87, contextRecall: 0.83, contextPrecision: 0.87 },
  { date: '2026-05-13', faithfulness: 0.90, answerRelevancy: 0.89, contextRecall: 0.85, contextPrecision: 0.88 },
  { date: '2026-05-20', faithfulness: 0.93, answerRelevancy: 0.91, contextRecall: 0.87, contextPrecision: 0.90 },
]

export const segmentLabels: Record<string, string> = {
  pricing_objection: 'Pricing Objection',
  timing_issue: 'Timing Issue',
  competitor_loss: 'Competitor Loss',
  ghosted: 'Ghosted',
  no_decision_maker: 'No Decision Maker',
  budget_constraints: 'Budget Constraints',
  feature_gap: 'Feature Gap',
  unknown: 'Unknown',
}

export const segmentColors: Record<string, string> = {
  pricing_objection: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  timing_issue: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  competitor_loss: 'bg-red-500/20 text-red-400 border-red-500/30',
  ghosted: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  no_decision_maker: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  budget_constraints: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  feature_gap: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
  unknown: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
}

export const statusColors: Record<string, string> = {
  dormant: 'bg-red-500/20 text-red-400 border-red-500/30',
  active: 'bg-green-500/20 text-green-400 border-green-500/30',
  reactivated: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  lost: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  meeting_booked: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
}
