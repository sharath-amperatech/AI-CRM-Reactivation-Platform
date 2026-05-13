# ReactivIQ — AI CRM Reactivation Platform

> Recover lost revenue from dormant CRM leads using AI-powered reactivation workflows, contextual personalization, and intelligent automation.

---

<p align="center">
  <img src="./docs/banner.png" alt="ReactivIQ Banner" width="100%" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-Backend-green" />
  <img src="https://img.shields.io/badge/React-Frontend-blue" />
  <img src="https://img.shields.io/badge/LangGraph-Workflow-purple" />
  <img src="https://img.shields.io/badge/OpenAI-LLM-black" />
  <img src="https://img.shields.io/badge/PostgreSQL-Database-blue" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

---

# Overview

ReactivIQ is an AI-powered CRM reactivation platform designed to help businesses recover revenue from dormant leads.

Instead of letting old leads sit untouched in CRMs like HubSpot or Salesforce, ReactivIQ automatically:

* detects stale opportunities
* retrieves historical CRM context
* generates personalized outreach
* automates follow-up workflows
* handles replies intelligently
* books meetings
* tracks recovered pipeline revenue

Built with:

* FastAPI
* React
* LangChain
* LangGraph
* PostgreSQL
* PGVector
* OpenAI APIs

---

# Why ReactivIQ?

Most companies spend heavily acquiring leads but fail to consistently follow up.

ReactivIQ transforms old CRM records into:

## “recoverable revenue opportunities”

The platform combines:

* AI personalization
* CRM memory retrieval (RAG)
* workflow orchestration
* human-in-the-loop approvals
* multi-step automation

to create production-grade reactivation systems.

---

# Core Features

## AI Dormant Lead Detection

Automatically identify:

* stale leads
* ghosted opportunities
* no-show leads
* inactive pipeline stages
* forgotten prospects

---

## CRM Memory-Aware Personalization

Retrieve:

* previous conversations
* CRM notes
* objections
* call summaries
* email history

before generating outreach.

This enables highly contextual AI messaging.

---

## AI Outreach Generation

Generate:

* personalized emails
* SMS campaigns
* WhatsApp messages

based on:

* lead history
* inactivity reasons
* CRM activity
* prior interactions

---

## Workflow Automation (LangGraph)

Build multi-step workflows like:

```text
Detect Dormant Lead
    ↓
Retrieve CRM Context
    ↓
Classify Lead
    ↓
Generate Personalized Outreach
    ↓
Human Approval
    ↓
Send Message
    ↓
Wait For Reply
    ↓
Analyze Response
    ↓
Book Meeting / Escalate
```

---

## Human-in-the-Loop (HITL)

Enterprise-safe AI workflows with:

* approval checkpoints
* confidence thresholds
* audit logs
* retry handling

---

## Revenue Recovery Dashboard

Track:

* recovered pipeline
* reactivation rates
* meetings booked
* campaign performance
* recovered revenue

---

# Architecture

```text
                ┌────────────────────┐
                │      React UI       │
                └─────────┬──────────┘
                          │
                    FastAPI Backend
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
      ▼                   ▼                   ▼
 LangChain          LangGraph          Celery Workers
  (LLMs)          (Workflow Engine)     (Async Jobs)

      │                   │                   │
      └───────────────────┼───────────────────┘
                          │
                  PostgreSQL + PGVector
                          │
      ┌───────────────────┼───────────────────┐
      ▼                   ▼                   ▼
   HubSpot             Twilio              Resend
   CRM API             SMS API             Email API
```

---

# Tech Stack

| Layer            | Technology                |
| ---------------- | ------------------------- |
| Frontend         | React + Tailwind + ShadCN |
| Backend          | FastAPI                   |
| AI Framework     | LangChain                 |
| Workflow Engine  | LangGraph                 |
| Database         | PostgreSQL                |
| Vector Store     | PGVector                  |
| Async Processing | Celery + Redis            |
| CRM Integration  | HubSpot API               |
| Messaging        | Twilio                    |
| Email            | Resend                    |
| Authentication   | Clerk/Auth0               |
| LLM Provider     | OpenAI                    |

---

# Project Structure

```bash
reactiviq/
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── workflows/
│   ├── agents/
│   ├── db/
│   ├── tasks/
│   └── integrations/
│
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── lib/
│
├── docs/
├── docker/
├── scripts/
└── README.md
```

---

# MVP Features

## Phase 1

* [x] HubSpot Integration
* [x] Dormant Lead Detection
* [x] AI Email Generation
* [x] Lead Segmentation
* [x] Workflow Engine
* [x] Human Approval System
* [x] Analytics Dashboard

---

## Planned Features

* [ ] WhatsApp Integration
* [ ] AI Voice Agents
* [ ] Multi-CRM Support
* [ ] Predictive Lead Scoring
* [ ] AI SDR Workflows
* [ ] Multi-Agent Systems
* [ ] Revenue Forecasting

---

# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/reactiviq.git

cd reactiviq
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

source venv/bin/activate
# Windows:
# venv\Scripts\activate

pip install -r requirements.txt
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## Environment Variables

Create `.env` files for backend and frontend.

### Backend `.env`

```env
OPENAI_API_KEY=
DATABASE_URL=
REDIS_URL=
HUBSPOT_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
RESEND_API_KEY=
```

---

# Running The Application

## Start Backend

```bash
uvicorn main:app --reload
```

---

## Start Celery Worker

```bash
celery -A tasks worker --loglevel=info
```

---

## Start Frontend

```bash
npm run dev
```

---

# Example Workflow

## Reactivating Dormant Leads

1. Sync CRM leads
2. Detect inactive leads
3. Retrieve historical CRM context
4. Generate AI-personalized outreach
5. Review & approve messages
6. Send campaign
7. Analyze replies
8. Book meetings automatically
9. Track recovered revenue

---

# LangGraph Workflow Example

```python
workflow = StateGraph()

workflow.add_node("fetch_leads", fetch_dormant_leads)
workflow.add_node("retrieve_context", retrieve_crm_context)
workflow.add_node("generate_message", generate_message)
workflow.add_node("approval", human_approval)
workflow.add_node("send_message", send_message)

workflow.add_edge("fetch_leads", "retrieve_context")
workflow.add_edge("retrieve_context", "generate_message")
workflow.add_edge("generate_message", "approval")
workflow.add_edge("approval", "send_message")
```

---

# Security & Compliance

* OAuth2 authentication
* Role-based access control
* Encrypted secrets
* Audit logging
* Human approval checkpoints
* GDPR-ready architecture
* AI confidence thresholds

---

# Design Principles

ReactivIQ follows:

* deterministic AI workflows
* human-in-the-loop systems
* durable execution patterns
* contextual retrieval
* workflow-first architecture

NOT:

* fully autonomous AI agents
* uncontrolled LLM execution

---

# Screenshots

> Add screenshots/gifs here

```text
/docs/screenshots/dashboard.png
/docs/screenshots/workflow-builder.png
/docs/screenshots/campaigns.png
```

---

# Roadmap

## V1

* CRM sync
* AI outreach
* workflow automation
* analytics dashboard

## V2

* AI reply handling
* omnichannel outreach
* predictive scoring

## V3

* AI SDR workflows
* voice agents
* multi-agent orchestration

---

# License

MIT License

---

# Inspiration

ReactivIQ is inspired by the growing shift toward:

* AI workflow systems
* revenue operations automation
* CRM intelligence
* enterprise AI orchestration

rather than generic chatbot applications.

---

# Acknowledgements

Built using:

* [LangChain](https://www.langchain.com?utm_source=chatgpt.com)
* [LangGraph](https://www.langchain.com/langgraph?utm_source=chatgpt.com)
* [FastAPI](https://fastapi.tiangolo.com?utm_source=chatgpt.com)
* [React](https://react.dev?utm_source=chatgpt.com)
* [PostgreSQL](https://www.postgresql.org?utm_source=chatgpt.com)

---
