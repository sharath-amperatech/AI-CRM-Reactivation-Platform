**ReactivIQ**

AI CRM Reactivation Platform

Product Requirements Document | Version 2.0

_Recover lost revenue from dormant CRM leads using AI-powered reactivation_

_workflows, contextual personalization, and intelligent automation._

**Prepared for**

Engineering Team

**Status**

Draft — MVP Build Ready

**Version**

v2.0 — Updated with GenAI Best Practices

**Date**

May 2026

**What's New in v2.0**

This version adds production-grade GenAI best practices identified against the GenAI Developer Roadmap 2025-2026:

*   F9 — RAG Evaluation Framework (RAGAS + Golden Dataset)
*   F10 — AI Observability & Tracing (Langfuse)
*   F3 Enhanced — Reranking, Parent-Child Chunking, HyDE retrieval
*   F4 Enhanced — Prompt versioning, model fallback chain, semantic caching
*   F11 — Embedding Versioning & Re-indexing Strategy

# **1\. Introduction & Goals**

## **1.1 Product Overview**

ReactivIQ is an AI-powered CRM reactivation platform designed to help businesses recover pipeline revenue from dormant leads. Rather than spending budget on new lead acquisition, ReactivIQ automatically identifies stale contacts in HubSpot, retrieves full historical CRM context, generates deeply personalized outreach, and orchestrates multi-step follow-up campaigns — all with human-in-the-loop approval gates.

Built on FastAPI, LangGraph, and OpenAI, ReactivIQ combines RAG-based CRM memory retrieval with deterministic workflow orchestration to produce enterprise-safe, measurable revenue recovery. v2.0 adds production-grade AI quality measurement, observability, and retrieval best practices aligned with the GenAI Developer Roadmap 2025–2026.

## **1.2 Elevator Pitch**

ReactivIQ is an AI-powered CRM reactivation platform that automatically identifies dormant leads, generates personalized outreach using historical CRM context, and orchestrates multi-step follow-up workflows to help businesses recover lost pipeline revenue — without generating new leads.

## **1.3 Primary Goals**

*   Recover Revenue: Enable businesses to surface and convert dormant pipeline from existing CRM data.
*   Automate Reactivation: Reduce manual follow-up effort through AI-generated campaigns and LangGraph workflows.
*   Improve Sales Efficiency: Allow SDR teams to focus on qualified, engaged leads rather than cold outreach.
*   Build AI Sales Memory: Use CRM history and vector retrieval (RAG) to generate intelligent, contextual communication.
*   **★** Measure AI Quality: Systematically evaluate RAG faithfulness, retrieval accuracy, and generation quality using RAGAS.
*   **★** Ensure Observability: Trace every AI call, retrieval step, and workflow node in production for continuous improvement.

## **1.4 Vision Statement**

Help businesses recover lost revenue from dormant CRM leads using AI-driven personalization, automated workflows, and intelligent re-engagement — making every stale lead a second chance.

# **2\. User Roles & Permission Matrix**

## **2.1 Role Definitions**

### **Admin**

*   Full platform access: CRM connections, billing, user management, all campaigns, all analytics.
*   Can create/delete workspaces and manage integrations.
*   Typical persona: Founder, RevOps Lead, Agency Owner.

### **Sales Manager**

*   Can create and manage campaigns, view team analytics, approve/reject AI-generated messages.
*   Cannot manage billing or other users.
*   Typical persona: VP Sales, Sales Manager, Agency Account Lead.

### **SDR (Sales Development Rep)**

*   Can view assigned leads, review AI drafts, approve messages, log replies, book meetings.
*   Cannot create campaigns or view revenue dashboard.
*   Typical persona: SDR, BDR, Sales Rep.

### **Read-Only**

*   Can view campaigns, lead statuses, and analytics. No write access.
*   Typical persona: Executive stakeholder, Client (agency context).

## **2.2 Permission Matrix**

**Feature / Action**

**Admin**

**Sales Mgr**

**SDR**

**Read-Only**

**Notes**

Connect / manage CRM (HubSpot)

Yes

No

No

No

Manage users & roles

Yes

No

No

No

Manage billing & subscription

Yes

No

No

No

Create / edit campaigns

Yes

Yes

No

No

View all campaigns

Yes

Yes

Own only

Yes

Approve AI-generated messages

Yes

Yes

Yes

No

Edit AI-generated messages

Yes

Yes

Yes

No

Trigger campaign send

Yes

Yes

No

No

View dormant lead list

Yes

Yes

Yes

Yes

Manually reclassify lead segment

Yes

Yes

Yes

No

View revenue recovery dashboard

Yes

Yes

No

Yes

Export analytics reports

Yes

Yes

No

No

View audit log

Yes

Yes

No

No

Log meeting / reply outcome

Yes

Yes

Yes

No

View AI quality dashboard ★

Yes

Yes

No

No

**NEW**

View Langfuse traces ★

Yes

No

No

No

**NEW**

# **3\. Feature Specifications**

## **F1 — CRM Integration (HubSpot)**

Connect user HubSpot accounts via OAuth 2.0 and incrementally sync all relevant CRM data into the ReactivIQ PostgreSQL database.

### **Functional Requirements**

*   OAuth 2.0 flow with HubSpot; store and refresh tokens securely.
*   Initial full sync: contacts, companies, deals, activities (emails, calls, notes, meetings).
*   Incremental sync via Celery task every 15 minutes (configurable).
*   Sync status indicator in UI: last synced timestamp, record counts, error states.
*   Webhook listener for real-time HubSpot events (deal stage changes, new contacts).
*   Map HubSpot custom properties to ReactivIQ lead schema.
*   Support multiple HubSpot portals per organization (agency use case).

### **Out of Scope — V1**

*   Salesforce, Zoho, Pipedrive, GoHighLevel (Phase 2+).

## **F2 — Dormant Lead Detection & Segmentation**

Automatically identify inactive leads based on configurable inactivity rules, then use AI to classify the root cause of inactivity.

### **Detection Rules**

*   No CRM activity logged in X days (default: 30 days, configurable 7–180).
*   Deal stage stuck for Y days (configurable per stage).
*   Lead marked as Lost or No-show in HubSpot.
*   Email opened but no reply within Z days.
*   Meeting booked but no follow-up activity after meeting date.

### **AI Segmentation Categories**

*   Pricing Objection — lead raised cost concerns.
*   Timing Issue — lead said not the right time.
*   Competitor Loss — lead chose a competitor.
*   Ghosted — no response after initial engagement.
*   No Decision Maker — contact lacks authority.
*   Budget Constraints — funding/budget issues flagged.
*   Feature Gap — product did not meet requirements.
*   Unknown — insufficient data to classify.

### **Functional Requirements**

*   Run detection job on full lead database daily (Celery beat scheduler).
*   LangChain LLM pipeline reads CRM notes, email summaries, call logs to classify lead.
*   Confidence score (0–1.0) stored per classification; display in UI.
*   Users can manually override AI classification.
*   Filter/sort dormant list by: segment, inactivity duration, deal value, last activity date.
*   Bulk selection for campaign enrollment.
*   **★** All segmentation LLM calls traced via Langfuse with input, output, model version, and latency.
*   **★** Segmentation accuracy tracked against golden dataset; alert if accuracy drops below 85%.

## **F3 — RAG-Based CRM Memory Retrieval ★ NEW**

**v2.0 ENHANCED**

_This feature has been significantly upgraded with production-grade retrieval techniques: parent-child chunking, reranking, HyDE, and embedding versioning. These changes are expected to improve retrieval accuracy by 15–30%._

Before generating any outreach, the AI retrieves relevant historical CRM context for each lead using a multi-stage retrieval pipeline over embedded CRM data stored in PGVector.

### **3a. Chunking Strategy (Updated)**

CRM activities are chunked using a parent-child strategy for optimal retrieval precision and context quality:

*   Child chunks: 256-token segments with 50-token overlap — used for embedding and similarity search.
*   Parent chunks: 1024-token segments — returned to the LLM as context after child retrieval.
*   Activity-aware splitting: short call notes (<100 tokens) stored as single chunks; long email threads split at sentence boundaries.
*   **★** Chunk size and overlap are treated as hyperparameters. Baseline: child=256, overlap=50. Tune based on RAGAS context recall scores from the evaluation framework (F9).

### **3b. Embedding & Storage**

*   CRM activities (emails, call notes, meeting summaries, deal notes) chunked using parent-child strategy and embedded using OpenAI text-embedding-3-small.
*   Embeddings stored in PGVector with metadata: lead\_id, activity\_type, date, sentiment, chunk\_version, parent\_chunk\_id.
*   **★** Embedding version tracked per chunk (see F11 — Embedding Versioning). All chunks carry an embedding\_model\_version field to support re-indexing on model upgrades.

### **3c. Retrieval Pipeline (Multi-Stage)**

Retrieval is now a three-stage pipeline:

*   Stage 1 — Candidate Retrieval: embed the query, run cosine similarity search in PGVector, retrieve top-50 child chunks for the given lead\_id.
*   **★** Stage 1b — HyDE (Hypothetical Document Embeddings): for leads with sparse history (<5 chunks), generate a hypothetical relevant CRM note using the lead's segment and profile, embed that, and use it as the retrieval query instead of the raw input. Significantly improves recall for sparse lead histories.
*   **★** Stage 2 — Reranking: pass top-50 candidates through Cohere Rerank API (or BGE-Reranker-v2 as local fallback) to rerank by relevance. Return top-5 reranked chunks.
*   Stage 3 — Parent Expansion: for each top-5 child chunk, retrieve the corresponding parent chunk (1024 tokens) and inject into the LLM context. This gives retrieval precision with full context quality.

### **3d. Functional Requirements**

*   Retrieval latency target: <700ms per lead (including reranking stage).
*   Store retrieved context snapshot (child chunk IDs + parent chunk content) in Message record for audit purposes.
*   Configurable top-K candidates for reranking (default: 50 candidates → rerank → top-5).
*   **★** Retrieval steps traced in Langfuse: query, candidate count, reranker scores, final chunks selected, latency per stage.
*   **★** Reranker can be disabled per environment (dev: skip for speed; prod: always on).

## **F4 — AI Personalized Outreach Generation ★ NEW**

**v2.0 ENHANCED**

_Adds prompt versioning, model fallback chain, semantic caching, and structured output validation. These changes improve reliability, reduce cost at scale, and enable systematic prompt improvement._

Generate highly personalized outreach messages for each dormant lead using retrieved CRM context, lead segment classification, and configurable tone/channel settings.

### **Supported Channels**

*   Email (via Resend API).
*   SMS (via Twilio API).
*   WhatsApp — Phase 2.

### **AI Inputs**

*   Lead profile: name, company, role, deal value, lead source.
*   Inactivity segment + confidence score.
*   Top-K retrieved CRM context chunks (parent chunks from RAG pipeline).
*   Campaign template and tone selection (professional, friendly, urgent, casual).
*   Sender name and company context.
*   **★** Active prompt template version (from prompt version registry).

### **Functional Requirements**

*   Generate email subject + body; SMS message; structured output via JSON schema.
*   Prompt templates configurable per segment (pricing objection template vs. ghosted template etc.).
*   Users can regenerate messages up to 5 times with different variations.
*   All generated messages enter Human Approval queue before sending.
*   Hallucination guardrail: if retrieved context is sparse (<2 chunks), flag message for extra human review.
*   Store prompt, context used, model version, and output in Messages table for audit.
*   **★** Prompt Versioning: all prompt templates stored in a prompt\_versions table with version number, content hash, created\_at, and created\_by. Each Message record links to the prompt\_version\_id used. Enables A/B testing prompts and regression tracking.
*   **★** Model Fallback Chain: primary model is GPT-4o. If OpenAI returns a 5xx error or rate limit, automatically fall back to Claude Sonnet (Anthropic), then to a locally hosted Llama3 8B instance. LiteLLM used as the provider abstraction layer.
*   **★** Semantic Caching: before calling the LLM, hash the query embedding and check Redis for a cached response (cosine similarity threshold: 0.97). Cached responses served instantly, reducing redundant API calls for similar leads with similar histories. Cache TTL: 1 hour.
*   **★** Model Tiering: use GPT-4o-mini for AI segmentation classification (F2) and reply classification (F7). Reserve GPT-4o for full message generation. Estimated 60–70% cost reduction on high-volume classification tasks.

## **F5 — LangGraph Campaign Workflow Engine**

Multi-step reactivation campaigns built on LangGraph StateGraph with configurable delays, trigger conditions, and exit rules.

### **Workflow Node Types**

*   fetch\_leads — query dormant leads matching campaign criteria.
*   retrieve\_context — RAG pipeline (multi-stage: cosine + rerank + parent expand) to fetch CRM history per lead.
*   classify\_lead — AI segmentation.
*   generate\_message — personalized outreach creation.
*   human\_approval — pause workflow, surface message for review.
*   send\_message — dispatch via Resend / Twilio.
*   wait\_for\_reply — monitor inbound responses with configurable timeout.
*   analyze\_response — classify reply sentiment and intent.
*   book\_meeting — trigger calendar booking flow.
*   escalate — route to human SDR queue.

### **Functional Requirements**

*   Visual campaign builder UI: drag-and-drop steps, configure delay between steps.
*   Campaign exit conditions: reply received, meeting booked, lead manually removed, unsubscribe.
*   Workflow state persisted in PostgreSQL (durable execution).
*   Celery workers execute scheduled steps; Redis for state coordination.
*   A/B test support: 2 message variants per step with split percentage.
*   Campaign analytics: open rates, reply rates, meeting bookings, step-level drop-off.
*   **★** Every LangGraph node transition is traced in Langfuse as a span: inputs, outputs, latency, token cost.

## **F6 — Human-in-the-Loop (HITL) Approval System**

Every AI-generated message must pass through a human approval checkpoint before sending. No autonomous outreach.

### **Functional Requirements**

*   Approval inbox shows: lead name, company, message draft, CRM context snippets, AI confidence score, segment classification.
*   Actions: Approve, Edit & Approve, Reject, Reassign.
*   Bulk approve for high-confidence messages (confidence > 0.85 threshold, configurable).
*   Rejection triggers: message flagged for regeneration or manual draft.
*   Audit log entry created for every approval action: user, timestamp, action, message\_id.
*   Email notification to approver when new messages enter queue.
*   SLA timer: messages unapproved after 24h escalate to Admin.
*   **★** Approvers can see the Langfuse trace link for each message — showing exactly which CRM chunks were retrieved and how the generation was reasoned.

## **F7 — Reply Analysis & Appointment Booking**

Monitor inbound replies, classify intent, and auto-route to booking or escalation.

### **Reply Classification**

*   Interested / Ready to meet.
*   Objection (pricing, timing, feature).
*   Unsubscribe / Not interested.
*   Out of office / Redirect.
*   Ambiguous — needs human review.

### **Functional Requirements**

*   Inbound email parsed via Resend inbound webhook; SMS via Twilio webhook.
*   LLM classifies reply and confidence score.
*   Interested replies: auto-send meeting booking link (Google Calendar / Calendly).
*   Objection replies: generate AI response suggestion, route to approval queue.
*   Unsubscribes: immediately halt campaign, update CRM, log suppression.
*   Meeting bookings sync back to HubSpot as activity.
*   **★** Reply classification uses GPT-4o-mini (model tiering). Classification calls traced in Langfuse.

## **F8 — Revenue Recovery Analytics Dashboard**

Real-time metrics dashboard tracking campaign performance, recovered pipeline, and team productivity.

### **Dashboard Metrics**

*   Recovered pipeline value ($) — sum of deal values from reactivated leads.
*   Reactivation rate (%) — reactivated / total dormant leads contacted.
*   Meeting booking rate (%) — meetings booked / leads contacted.
*   Email open rate, reply rate, unsubscribe rate.
*   Campaign step-level performance waterfall.
*   Lead segment breakdown (which segments convert best).
*   SDR productivity: messages approved, meetings booked per rep.

### **Functional Requirements**

*   Real-time analytics via server-sent events or polling (10s refresh).
*   Date range filter: last 7/30/90 days, custom range.
*   Filter by campaign, channel, lead segment, SDR.
*   CSV/PDF export for reporting.
*   Revenue recovered widget on main dashboard with month-over-month comparison.

## **F9 — RAG Evaluation Framework ★ NEW**

**NEW in v2.0**

_Addresses the most critical gap from the GenAI Roadmap: systematic quality measurement. Without this, there is no way to know if RAG changes improve or degrade output quality._

A systematic evaluation framework using RAGAS metrics and a curated golden dataset to measure, track, and improve RAG retrieval and generation quality over time.

### **9.1 Golden Dataset**

*   Curate 100–200 Q&A pairs derived from representative CRM histories, covering all 8 lead segments.
*   Each pair: {lead\_id, query, ground\_truth\_answer, expected\_context\_sources}.
*   Dataset stored in golden\_dataset table; versioned alongside prompt versions.
*   Expanded over time; minimum 20 examples per lead segment.
*   **★** Golden dataset is the regression test suite. Run on every significant change to chunking, embeddings, prompts, or retrieval pipeline.

### **9.2 RAGAS Metrics**

**Metric**

**What It Measures**

**How Computed**

**Target**

Faithfulness

Are all claims in the answer supported by retrieved context? Catches hallucination.

LLM-as-judge: does answer contain facts not in context?

\> 0.85

Answer Relevancy

Does the answer actually address what was asked?

Embed answer + query, measure cosine similarity.

\> 0.80

Context Recall

Did retrieval find the chunks needed to answer?

Compare retrieved chunks vs ground truth answer.

\> 0.75

Context Precision

Are retrieved chunks actually relevant? Measures retrieval noise.

% of retrieved chunks useful for the question.

\> 0.70

### **9.3 Evaluation Schedule**

*   Nightly automated run: RAGAS evaluation on 100 random production traces from the prior day (sampled via Langfuse).
*   PR-gated regression: every pull request that modifies chunking, prompts, retrieval, or embedding runs the full golden dataset eval via GitHub Actions. PR blocked if any metric drops >5% from baseline.
*   Metric history stored in eval\_runs table; charted in AI Quality Dashboard.
*   **★** Alert policy: if faithfulness drops below 0.80 for 3 consecutive nightly runs, fire PagerDuty alert to on-call engineer.

### **9.4 AI Quality Dashboard**

New dashboard page (/quality) showing:

*   RAGAS metric trends over time (line charts per metric).
*   Worst-performing queries from nightly eval — sorted by faithfulness score.
*   Prompt version comparison: side-by-side metric comparison when a new prompt version is deployed.
*   Retrieval quality: context recall and precision trends; flag if reranker is degrading.
*   Golden dataset coverage: which segments have the most/least test coverage.

## **F10 — AI Observability & Tracing (Langfuse) ★ NEW**

**NEW in v2.0**

_Addresses the second critical gap: production visibility. Without tracing, debugging quality issues, cost overruns, and latency spikes is guesswork._

Langfuse (self-hosted) provides full observability over every LLM call, RAG retrieval step, and LangGraph workflow execution in production.

### **10.1 What is Traced**

**Component**

**Trace Data Captured**

**Langfuse Object**

AI Segmentation (F2)

Lead ID, CRM text input, segment output, confidence, model, latency, cost

Trace → Generation span

RAG Retrieval (F3)

Query, candidate count, reranker scores, top-5 chunk IDs, latency per stage

Trace → Retrieval span

Message Generation (F4)

Lead ID, prompt version, context chunks, model, output, tokens, cost, latency

Trace → Generation span

LangGraph Nodes (F5)

Node name, state in/out, transition time, errors

Trace → Span per node

Reply Classification (F7)

Reply text, classification output, confidence, model, latency

Trace → Generation span

### **10.2 Trace Schema**

Every trace includes these standard fields:

*   session\_id — campaign\_enrollment\_id or user session ID.
*   user\_id — org\_id + user\_id for tenant isolation.
*   lead\_id — for linking traces back to specific leads.
*   prompt\_version\_id — links to the active prompt template version.
*   model — exact model string used (e.g. gpt-4o-2024-08-06).
*   cost\_usd — computed from token counts and model pricing.
*   latency\_ms — end-to-end and per-stage latencies.

### **10.3 Langfuse Deployment**

*   Self-hosted Langfuse via Docker Compose (Postgres + Redis + Next.js frontend).
*   Tenant isolation: org\_id used as Langfuse project namespace. No cross-tenant trace leakage.
*   Retention: traces retained 90 days; cost and quality metrics aggregated to permanent tables.
*   **★** Langfuse SDK instrumented in the AI service layer — not in individual route handlers. Every function that calls an LLM or runs a retrieval is wrapped with @observe decorator.

### **10.4 Cost & Latency Dashboards**

*   Daily cost breakdown by: model, feature (segmentation / generation / reply), campaign, org.
*   P50/P95/P99 latency per pipeline stage.
*   Token usage trends — alert if daily spend exceeds configured budget threshold.
*   Monthly cost report exported to finance team (CSV).

## **F11 — Embedding Versioning & Re-indexing Strategy ★ NEW**

**NEW in v2.0**

_Prevents silent quality degradation when chunking strategies or embedding models change. Without this, stale embeddings cause retrieval to silently worsen over time._

A versioning and re-indexing system ensures that all embeddings in PGVector remain consistent with the current chunking strategy and embedding model. Any change to these triggers a controlled re-indexing job.

### **11.1 Embedding Version Registry**

*   embedding\_versions table: id, model\_name (e.g. text-embedding-3-small), chunk\_size, overlap, created\_at, is\_active.
*   Every chunk in crm\_activities carries an embedding\_version\_id foreign key.
*   Retrieval queries always filter by the active embedding\_version\_id to avoid mixing stale and current embeddings.

### **11.2 Re-indexing Workflow**

*   When a new embedding version is created (model upgrade or chunk strategy change), a Celery task is enqueued to re-embed all chunks in the background.
*   Blue-green re-indexing: new embeddings written to a shadow PGVector namespace. Old embeddings remain active until re-indexing is complete and RAGAS validation passes.
*   Cutover: admin triggers namespace swap after validation. Zero-downtime for active campaigns.
*   Re-indexing progress tracked in embedding\_jobs table: status, chunks\_processed, chunks\_total, started\_at, completed\_at.
*   **★** Re-indexing automatically triggers the RAGAS evaluation suite after completion. If context recall drops vs. the previous version, the cutover is blocked and an alert is fired.

### **11.3 Operational Rules**

*   Chunk size and overlap changes always require a new embedding version — never update in place.
*   Embedding model upgrades (e.g. text-embedding-3-small → 3-large) always require full re-indexing.
*   Production re-indexing jobs run with concurrency limits (max 4 workers) to avoid PGVector write contention.

# **4\. Database Schema**

PostgreSQL 15 with PGVector extension. SQLAlchemy ORM. All tables include created\_at (TIMESTAMPTZ) and updated\_at (TIMESTAMPTZ) with auto-update trigger.

**v2.0 ADDITIONS**

_New tables: prompt\_versions, embedding\_versions, embedding\_jobs, eval\_runs, golden\_dataset. Updated tables: crm\_activities (embedding\_version\_id, parent\_chunk\_id), messages (prompt\_version\_id, langfuse\_trace\_id)._

## **4.1 Core Entities (Unchanged)**

organizations, users, leads, crm\_activities, campaigns, campaign\_enrollments, messages, replies, bookings, audit\_logs — schemas unchanged from v1.0 except as noted below.

## **4.2 Updated Columns**

### **crm\_activities (updated)**

**Column**

**Type**

**Description**

**embedding\_version\_id**

UUID FK

References embedding\_versions.id — tracks which model/chunk config produced this embedding

**parent\_chunk\_id**

UUID FK

Self-referencing FK to parent chunk (null for parent chunks)

**chunk\_index**

INTEGER

Position of child chunk within parent chunk

### **messages (updated)**

**Column**

**Type**

**Description**

**prompt\_version\_id**

UUID FK

References prompt\_versions.id — which prompt template generated this message

**langfuse\_trace\_id**

VARCHAR(255)

Langfuse trace ID for this generation — enables deep link from approval UI to trace

**reranker\_scores**

JSONB

Reranker scores for top-K chunks at generation time

## **4.3 New Tables**

### **prompt\_versions**

**Column**

**Type**

**Description**

id

UUID PK

Primary key

template\_name

VARCHAR(100)

e.g. email\_ghosted, sms\_pricing\_objection

version\_number

INTEGER

Monotonically increasing per template\_name

content

TEXT

Full prompt template with variable placeholders

content\_hash

VARCHAR(64)

SHA-256 of content — detects accidental duplicates

is\_active

BOOLEAN

Only one active version per template\_name at a time

created\_by

UUID FK

References users.id

ragas\_scores

JSONB

Latest RAGAS evaluation scores for this prompt version

### **embedding\_versions**

**Column**

**Type**

**Description**

id

UUID PK

Primary key

model\_name

VARCHAR(100)

e.g. text-embedding-3-small

chunk\_size

INTEGER

Child chunk size in tokens

chunk\_overlap

INTEGER

Overlap in tokens between child chunks

parent\_chunk\_size

INTEGER

Parent chunk size in tokens

is\_active

BOOLEAN

Currently active embedding configuration

context\_recall\_score

NUMERIC(4,3)

RAGAS context recall at time of validation

### **eval\_runs**

**Column**

**Type**

**Description**

id

UUID PK

Primary key

run\_type

ENUM

nightly | pr\_gate | manual | embedding\_validation

prompt\_version\_id

UUID FK

Active prompt version during this run

embedding\_version\_id

UUID FK

Active embedding version during this run

faithfulness

NUMERIC(4,3)

RAGAS faithfulness score

answer\_relevancy

NUMERIC(4,3)

RAGAS answer relevancy score

context\_recall

NUMERIC(4,3)

RAGAS context recall score

context\_precision

NUMERIC(4,3)

RAGAS context precision score

samples\_evaluated

INTEGER

Number of Q&A pairs evaluated in this run

alerts\_fired

BOOLEAN

Whether a quality alert was triggered

### **golden\_dataset**

**Column**

**Type**

**Description**

id

UUID PK

Primary key

lead\_segment

VARCHAR(100)

Lead segment this example covers

query

TEXT

Test query / generation prompt

ground\_truth\_answer

TEXT

Expected ideal answer

expected\_chunk\_ids

UUID\[\]

CRM activity chunk IDs that should be retrieved

is\_active

BOOLEAN

Include in automated eval runs

created\_by

UUID FK

References users.id (human annotator)

# **5\. UI/UX Specifications**

## **5.1 Design Direction**

Authoritative, data-dense, enterprise-clean. Feels like a revenue operations command center — not a generic SaaS dashboard. Reference: Linear meets Salesforce.

## **5.2 Color System**

**Token**

**Hex**

**Tailwind Class**

Primary Background

#0F172A (Navy)

bg-slate-900

Surface / Card

#1E293B

bg-slate-800

Accent Blue

#3B82F6

text-blue-500

Accent Blue Light

#DBEAFE

bg-blue-100

Muted Text

#64748B

text-slate-500

Border

#334155

border-slate-700

Success Green

#22C55E

text-green-500

Warning Amber

#F59E0B

text-amber-500

Danger Red

#EF4444

text-red-500

## **5.3 Typography**

*   Font Family: Inter (Google Fonts) — headings and body.
*   Monospace: JetBrains Mono — code blocks, JSON previews.
*   H1: text-3xl font-bold tracking-tight (30px).
*   H2: text-xl font-semibold (20px).
*   Body: text-sm (14px), text-slate-300 on dark backgrounds.
*   Labels: text-xs font-medium uppercase tracking-wider text-slate-500.

## **5.4 Core Pages & Navigation**

**Route**

**Page / Description**

/dashboard

Revenue Recovery Dashboard — KPI cards, recent campaign activity, pipeline chart.

/leads

Dormant Lead List — filterable table with segment badges, deal value, inactivity duration.

/leads/:id

Lead Detail — full CRM history timeline, AI classification, message history.

/campaigns

Campaign List — status, leads enrolled, performance stats.

/campaigns/new

Campaign Builder — step editor, lead targeting filters, workflow config.

/campaigns/:id

Campaign Detail — step-level analytics, enrolled leads, activity feed.

/approvals

Approval Inbox — message review queue with inline edit, approve/reject.

/analytics

Analytics — deeper charts: response rates, segment performance, SDR leaderboard.

/settings

Settings — CRM connections, team management, billing, AI configuration.

**/quality ★**

AI Quality Dashboard — RAGAS metric trends, worst-performing queries, prompt version comparison, retrieval quality stats. Admin + Sales Manager only.

## **5.5 Key Components (ShadCN/Tailwind)**

*   LeadSegmentBadge — color-coded pill per segment type.
*   ConfidenceScore — progress bar + numeric (0.0–1.0) with color thresholds.
*   MessageDraftCard — approval card showing lead context, message, AI inputs, inline edit, approve/reject buttons.
*   WorkflowStepEditor — drag-and-drop step list with delay config and node type selector.
*   CRMTimelineItem — collapsible activity entry with icon, date, and content snippet.
*   RevenueKPICard — large number, delta vs. prior period, trend sparkline.
*   **★** RAGASMetricCard — sparkline chart for a single RAGAS metric (faithfulness, relevancy, recall, precision) with trend direction indicator and alert threshold line.
*   **★** TraceLink — inline component in MessageDraftCard showing a clickable Langfuse trace deep-link so approvers can inspect exactly how a message was generated.

# **6\. Tech Stack & Integration Specs**

## **6.1 Full Stack Overview**

**Layer**

**Technology**

**Notes**

Frontend

React 18 + Vite

TypeScript, Tailwind CSS v3, ShadCN/UI

Backend

FastAPI (Python 3.11)

Async endpoints, Pydantic v2 validation

AI Orchestration

LangChain 0.2

LLM chains, prompt templates, output parsers

Workflow Engine

LangGraph 0.1

Stateful multi-step campaign execution

LLM Provider (Primary)

OpenAI GPT-4o

chat/completions + text-embedding-3-small

**LLM Fallback Chain ★**

GPT-4o → Claude Sonnet → Llama3 8B (local)

LiteLLM for provider abstraction. Auto-failover on 5xx or rate limit.

**Model Tiering ★**

GPT-4o-mini for classification; GPT-4o for generation

~60-70% cost reduction on classification tasks.

Database

PostgreSQL 15

SQLAlchemy ORM + Alembic migrations

Vector Store

PGVector

pgvector extension on same Postgres instance

**Reranker ★**

Cohere Rerank API / BGE-Reranker-v2 (local fallback)

Post-retrieval reranking. +15-30% answer quality.

Async Queue

Celery + Redis

Background jobs, campaign scheduling

**Semantic Cache ★**

Redis (cosine similarity on embeddings)

Cache LLM responses for similar queries. TTL: 1 hour.

**Observability ★**

Langfuse (self-hosted)

Full LLM + RAG + workflow tracing in production.

**RAG Evaluation ★**

RAGAS + Golden Dataset

Nightly evals + PR-gated regression testing.

Authentication

Clerk

JWT, OAuth, RBAC

CRM

HubSpot API v3

OAuth 2.0, contacts/deals/activities

Email

Resend API

Outbound send + inbound webhook

SMS

Twilio API

Outbound SMS + inbound webhook

Containerization

Docker + Docker Compose

Local dev + staging deployments

## **6.2 Updated Project Structure**

New directories added in v2.0:

*   **★** backend/evaluation/ — RAGAS eval runner, golden dataset loader, nightly eval Celery task, GitHub Actions integration.
*   **★** backend/observability/ — Langfuse SDK setup, @observe decorator helpers, trace schema definitions.
*   **★** backend/prompt\_registry/ — Prompt version CRUD, active version loader, content hashing.
*   **★** backend/reranker/ — Cohere Rerank client, BGE-Reranker local fallback, score normalization.
*   **★** backend/cache/ — Semantic cache implementation (Redis + embedding cosine similarity).

# **7\. LangGraph Workflow Architecture**

## **7.1 State Schema**

class ReactivationState(TypedDict):

*   lead\_id: str
*   lead\_data: dict
*   crm\_context: list\[dict\] # Retrieved parent chunks from multi-stage RAG
*   retrieval\_metadata: dict # Reranker scores, chunk IDs, stage latencies
*   segment: str
*   segment\_confidence: float
*   message\_draft: dict # {subject, body, channel}
*   prompt\_version\_id: str # Active prompt version used
*   langfuse\_trace\_id: str # For linking approval UI to trace
*   approval\_status: str # pending | approved | rejected
*   send\_result: dict
*   reply: dict | None
*   reply\_classification: str
*   booking: dict | None
*   error: str | None

## **7.2 Node Definitions**

**Node**

**Function**

**Output / State Mutation**

fetch\_lead

Load lead + CRM profile from DB

Sets lead\_data

retrieve\_context

Multi-stage RAG: cosine search → HyDE (if sparse) → Cohere reranking → parent expansion

Sets crm\_context (top-5 parent chunks) + retrieval\_metadata

classify\_lead

GPT-4o-mini classifies inactivity reason (model tiering)

Sets segment, segment\_confidence

generate\_message

GPT-4o generates personalized outreach using active prompt version; checks semantic cache first

Sets message\_draft, prompt\_version\_id, langfuse\_trace\_id

human\_approval

Interrupt + persist; await user action in approval UI

Sets approval\_status

send\_message

Dispatch via Resend / Twilio

Sets send\_result; updates Message record

wait\_for\_reply

Poll DB for inbound reply (configurable timeout)

Sets reply or times out

analyze\_response

GPT-4o-mini classifies reply intent (model tiering)

Sets reply\_classification

book\_meeting

Send Calendly link; await booking webhook

Sets booking; updates CRM

escalate

Route to SDR queue for manual follow-up

Creates Escalation record

## **7.3 Durable Execution & Observability**

*   Workflow state is persisted to the campaign\_enrollments table after every node transition.
*   If a Celery worker crashes, the workflow resumes from the last completed node on restart.
*   The human\_approval node uses LangGraph's interrupt() mechanism, serializing state to the database and yielding until the API receives an approval action.
*   **★** Every node execution opens a Langfuse span. The full trace for a lead's reactivation journey — from retrieval through approval to send — is visible as a single Langfuse trace tree.

# **8\. AI Guardrails & Safety Controls**

## **8.1 Human-in-the-Loop Requirements**

*   MANDATORY: No AI-generated message is ever sent without explicit human approval. This is non-negotiable for V1.
*   Bulk approval only available for messages with confidence score >= 0.85 (configurable per org).
*   Messages with < 2 RAG context chunks retrieved are flagged REVIEW REQUIRED regardless of confidence.
*   Messages referencing PII not present in CRM context are auto-rejected by validation layer.

## **8.2 Hallucination Prevention**

*   Prompt template instructs model to ONLY reference facts present in the provided CRM context. Never invent meeting dates, deal values, or product features.
*   Output parsed with Pydantic schema; if model produces content not grounded in retrieved context, generation is flagged.
*   Context chunks attached to each Message record; approver can inspect exactly what data the AI used.
*   **★** RAGAS faithfulness score computed for a random sample of generated messages nightly — alerts if score drops below 0.80.

## **8.3 PII Protection**

*   API keys and OAuth tokens encrypted at rest using Fernet symmetric encryption.
*   CRM activity embeddings stored without raw PII in vector metadata.
*   Audit log captures all data access events.
*   GDPR: lead suppression list enforced before any message generation; suppressed leads are skipped automatically.
*   **★** Langfuse traces are stored in self-hosted infrastructure; no CRM data or PII is sent to third-party observability vendors.

## **8.4 Confidence Thresholds**

**Confidence Range**

**Action**

**UI Indicator**

0.85 – 1.00

Eligible for bulk approve

Green badge

0.60 – 0.84

Individual review required

Amber badge

0.00 – 0.59

Flagged — extra review + edit recommended

Red badge

## **8.5 Rate Limits & Compliance**

*   Daily send limit configurable per campaign (default: 50 messages/day/campaign).
*   CAN-SPAM: all emails include unsubscribe footer; unsubscribes processed within minutes (automated).
*   Twilio SMS: honor STOP keyword; automatic suppression.
*   All AI actions logged in audit\_logs with user\_id, timestamp, prompt\_snapshot, and model\_version.
*   **★** LiteLLM model fallback is logged in audit\_logs with reason (rate\_limit | 5xx | timeout) so engineers can identify chronic provider issues.

# **9\. MVP vs. Future Phases**

## **9.1 MVP Scope (7 Weeks — Updated)**

**v2.0 NOTE**

_Evaluation and observability infrastructure (F9, F10) are added to Week 1 setup. These are foundational — they must be instrumented before any AI features are built, not added as an afterthought._

**Week**

**Deliverable**

**Features**

Week 1

Foundation + CRM + Observability

Auth, HubSpot OAuth, Lead sync, DB migrations, Langfuse self-hosted setup, @observe decorator instrumentation, Langfuse project config

Week 2

AI Detection + RAG Pipeline

Dormant detection, AI segmentation (GPT-4o-mini), parent-child chunking, PGVector embedding, Cohere reranker integration, HyDE for sparse leads

Week 3

Message Generation + Prompt Registry

Outreach generation, prompt versioning system, LiteLLM fallback chain, semantic cache, HITL approval system

Week 4

LangGraph Workflow Engine

Campaign builder, step execution, durable state, full workflow Langfuse tracing

Week 5

Send + Reply Handling

Resend/Twilio integration, reply ingestion, reply classification (GPT-4o-mini), meeting booking

Week 6

Evaluation Framework

Golden dataset curation (100+ examples), RAGAS nightly eval, PR gate GitHub Action, AI Quality Dashboard, eval\_runs table, alert policies

Week 7

Analytics Dashboard + QA

Revenue dashboard, export, load testing (Locust p95 latencies), end-to-end QA, Docker setup, embedding versioning

## **9.2 Priority Matrix**

**Feature**

**Priority**

**Phase**

HubSpot OAuth + Lead Sync

P0 — Critical

MVP

Dormant Lead Detection

P0 — Critical

MVP

AI Segmentation (GPT-4o-mini)

P0 — Critical

MVP

RAG CRM Memory — Parent-Child Chunking

P0 — Critical

MVP

Cohere Reranking (Post-Retrieval)

P0 — Critical

MVP

AI Email Generation

P0 — Critical

MVP

Human Approval System (HITL)

P0 — Critical

MVP

LangGraph Campaign Workflow

P0 — Critical

MVP

Email Send (Resend)

P0 — Critical

MVP

**Langfuse Observability ★**

P0 — Critical

MVP

**Prompt Versioning System ★**

P0 — Critical

MVP

**LiteLLM Model Fallback Chain ★**

P0 — Critical

MVP

SMS Send (Twilio)

P1 — High

MVP

Revenue Recovery Dashboard

P1 — High

MVP

Reply Classification

P1 — High

MVP

Meeting Booking (Calendly)

P1 — High

MVP

**RAGAS Evaluation Framework ★**

P1 — High

MVP

**Golden Dataset (100+ examples) ★**

P1 — High

MVP

**AI Quality Dashboard ★**

P1 — High

MVP

**Semantic Caching (Redis) ★**

P1 — High

MVP

**HyDE for Sparse Lead Retrieval ★**

P1 — High

MVP

**Embedding Versioning (F11) ★**

P1 — High

MVP

**Load Testing (Locust) ★**

P1 — High

MVP

WhatsApp Integration

P2 — Medium

Phase 2

Salesforce / Zoho CRM

P2 — Medium

Phase 2

Predictive Lead Scoring

P2 — Medium

Phase 3

AI Voice Agents

P3 — Low

Phase 4

# **10\. Non-Functional Requirements**

## **10.1 Performance**

*   AI message generation latency: < 5 seconds per lead (P95).
*   Dashboard page load: < 2 seconds (P95).
*   PGVector retrieval (pre-reranking): < 300ms per lead.
*   Reranking (Cohere API): < 400ms per lead.
*   Total RAG pipeline (retrieval + reranking + parent expansion): < 700ms.
*   HubSpot sync throughput: 1,000 records/minute.
*   **★** Latency targets validated via Locust load testing (Week 7): p50/p95/p99 measured at 50 concurrent users.

## **10.2 Scalability**

*   Support 100,000+ leads per organization.
*   Campaign workflows executed via Celery workers; horizontally scalable.
*   PGVector supports up to 1M vectors per instance; partition by org\_id for larger deployments.
*   **★** Semantic cache (Redis) reduces LLM calls under high-volume campaigns — measured as cache hit rate metric in Langfuse cost dashboard.

## **10.3 Security**

*   OAuth 2.0 authentication via Clerk.
*   All API routes require valid JWT; role checked per endpoint.
*   CRM tokens encrypted at rest using Fernet (AES-128).
*   HTTPS enforced; HSTS headers set.
*   Input sanitization on all LLM prompts to prevent prompt injection.
*   **★** Langfuse self-hosted deployment ensures no CRM data or PII leaves the infrastructure perimeter.
*   **★** Cohere Rerank API calls contain only chunk text (no lead PII). Lead IDs never sent to external reranking services.

## **10.4 Reliability**

*   Celery tasks include exponential backoff retry (max 3 retries).
*   Message delivery monitored via webhook callbacks; undelivered messages flagged.
*   Workflow state persisted to DB after every node; crash-safe resume.
*   Database backups: daily snapshot, 30-day retention.
*   **★** LiteLLM fallback chain ensures AI generation continues even if OpenAI is degraded. Fallback events logged and alerted.
*   **★** RAGAS nightly eval alert (faithfulness < 0.80 for 3 consecutive nights) provides an early warning system for quality degradation before users notice.

## **10.5 Compliance**

*   GDPR: right to erasure supported; lead suppression list enforced.
*   CAN-SPAM: unsubscribe link in all emails; processed immediately.
*   Twilio: STOP keyword suppression for SMS.
*   Full audit log for all AI actions (what was generated, who approved, when sent).
*   **★** GDPR data erasure: when a lead is erased, their crm\_activities embeddings are deleted from PGVector and their Langfuse traces are purged from the self-hosted instance.

# **11\. API Module Breakdown**

## **11.1 – 11.7 (Unchanged from v1.0)**

Authentication, CRM Integration, Leads, AI Service, Campaign, Message Approval, and Webhook Handler endpoints are unchanged from v1.0. Refer to v1.0 PRD for full endpoint specifications.

## **11.8 Analytics Service (Unchanged)**

*   GET /analytics/dashboard, /analytics/campaigns, /analytics/segments, /analytics/team, /analytics/export.

## **11.9 Quality & Observability Endpoints ★ NEW**

*   GET /quality/metrics — Current RAGAS scores (faithfulness, relevancy, recall, precision) with 30-day trend.
*   GET /quality/eval-runs — Paginated list of evaluation runs with scores and alert status.
*   POST /quality/eval-runs — Trigger a manual evaluation run (Admin only).
*   GET /quality/golden-dataset — List all golden dataset examples with coverage by segment.
*   POST /quality/golden-dataset — Add a new golden dataset example (Admin + Sales Manager).
*   GET /quality/prompt-versions — List all prompt versions with RAGAS scores per version.
*   POST /quality/prompt-versions — Create a new prompt version (Admin only).
*   PUT /quality/prompt-versions/:id/activate — Activate a prompt version (Admin only).
*   GET /quality/traces/:message\_id — Get Langfuse trace deep-link for a specific message.

## **11.10 Embedding Management Endpoints ★ NEW**

*   GET /embeddings/versions — List all embedding versions with status and RAGAS context recall.
*   POST /embeddings/versions — Create new embedding version (triggers re-indexing job).
*   GET /embeddings/jobs — List embedding re-indexing jobs with progress.
*   POST /embeddings/jobs/:id/cutover — Trigger namespace cutover after validation (Admin only).

# **12\. Success Metrics**

## **12.1 Business Metrics**

**Metric**

**Target**

Lead reactivation rate

10 – 20%

Meeting booking rate

5 – 10%

Response rate uplift vs. manual

+25% or greater

Reduction in manual follow-up effort

60%+ time saved

Recovered pipeline value

Track monthly; positive by Month 2

## **12.2 Product Metrics**

**Metric**

**Target**

CRM sync success rate

\> 99%

AI generation latency (P95)

< 5 seconds

Campaign message delivery success

\> 98%

AI segmentation accuracy

\> 85%

User retention (monthly)

\> 70%

Approval queue clearance time

< 24 hours median

**RAGAS Faithfulness Score ★**

**\> 0.85**

**RAGAS Context Recall ★**

**\> 0.75**

**RAGAS Answer Relevancy ★**

**\> 0.80**

**RAG Pipeline Latency (P95) ★**

**< 700ms end-to-end**

**LLM Cost per Campaign Message ★**

**Track weekly; optimize model tiering if > $0.02/msg**

**Semantic Cache Hit Rate ★**

**\> 15% under high-volume campaigns**

**Model Fallback Rate ★**

**< 2% of requests (signals OpenAI reliability)**

**ReactivIQ v2.0 — Build. Measure. Ship. Repeat.**

Confidential | Version 2.0 | May 2026