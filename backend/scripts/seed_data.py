#!/usr/bin/env python
"""Seed script: creates default org, users, and sample leads for local dev."""
from __future__ import annotations

import asyncio
import hashlib
import uuid
from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.base import get_session_factory
from app.models.crm_activity import ActivityType, CRMActivity
from app.models.embedding_version import EmbeddingVersion
from app.models.lead import Lead, LeadSegment, LeadStatus
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.services.activity_summary import generate_activity_summary, generate_lead_crm_summary
from app.services.embedding_service import EmbeddingService

# Fixed dev API key — used by the frontend in development (never use in production)
DEV_API_KEY = "riq_live_sk_dev_testing_key_for_local_development"
DEV_API_KEY_HASH = hashlib.sha256(DEV_API_KEY.encode()).hexdigest()

ORG_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
ADMIN_USER_ID = uuid.UUID("00000000-0000-4000-a000-000000000002")
USER_ALEX_ID = uuid.UUID("00000000-0000-4000-a000-000000000003")
USER_JORDAN_ID = uuid.UUID("00000000-0000-4000-a000-000000000004")
USER_SAM_ID = uuid.UUID("00000000-0000-4000-a000-000000000005")

# 20 leads seeded as if they arrived via HubSpotSyncService.sync_contacts()
# segment=UNKNOWN because classify_lead workflow node assigns the actual segment at runtime
HUBSPOT_LEADS = [
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000001"),
        hubspot_id="5821034",
        name="Ryan Nakamura",
        company="Finlink Technologies",
        email="ryan.nakamura@finlink.io",
        phone="+1 (415) 555-0721",
        role="VP of Finance",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=42000,
        inactive_days=94,
        last_activity_at=datetime(2026, 2, 24, tzinfo=timezone.utc),
        assigned_to_id=USER_ALEX_ID,
        industry="FinTech",
        company_size="50-200",
        location="San Francisco",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "OPEN",
            "lifecyclestage": "lead",
            "createdate": "2025-09-10T14:22:00Z",
            "lastmodifieddate": "2026-02-24T09:15:00Z",
            "num_associated_deals": 1,
            "hs_email_domain": "finlink.io",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000002"),
        hubspot_id="5821035",
        name="Isabella Torres",
        company="CareSync Health",
        email="i.torres@caresync.health",
        phone="+1 (512) 555-0833",
        role="Chief Medical Officer",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=78000,
        inactive_days=61,
        last_activity_at=datetime(2026, 3, 29, tzinfo=timezone.utc),
        assigned_to_id=USER_JORDAN_ID,
        industry="HealthTech",
        company_size="200-500",
        location="Austin",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:opportunity"],
        meta={
            "hs_lead_status": "IN_PROGRESS",
            "lifecyclestage": "opportunity",
            "createdate": "2025-11-03T09:40:00Z",
            "lastmodifieddate": "2026-03-29T11:00:00Z",
            "num_associated_deals": 1,
            "hs_email_domain": "caresync.health",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000003"),
        hubspot_id="5821036",
        name="Mohammed Al-Hassan",
        company="Atlas Precision Manufacturing",
        email="m.alhassan@atlasprecision.com",
        phone="+1 (216) 555-0492",
        role="Plant Director",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=31000,
        inactive_days=143,
        last_activity_at=datetime(2026, 1, 6, tzinfo=timezone.utc),
        assigned_to_id=USER_SAM_ID,
        industry="Manufacturing",
        company_size="500-2000",
        location="Cleveland",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "BAD_TIMING",
            "lifecyclestage": "lead",
            "createdate": "2025-07-22T08:10:00Z",
            "lastmodifieddate": "2026-01-06T15:30:00Z",
            "num_associated_deals": 0,
            "hs_email_domain": "atlasprecision.com",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000004"),
        hubspot_id="5821037",
        name="Sophie Dubois",
        company="Éclat Commerce",
        email="sophie.dubois@eclat.co",
        phone="+1 (212) 555-0654",
        role="Head of Digital",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=54000,
        inactive_days=108,
        last_activity_at=datetime(2026, 2, 9, tzinfo=timezone.utc),
        assigned_to_id=USER_ALEX_ID,
        industry="Retail Tech",
        company_size="200-500",
        location="New York",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "OPEN",
            "lifecyclestage": "lead",
            "createdate": "2025-08-15T13:55:00Z",
            "lastmodifieddate": "2026-02-09T10:20:00Z",
            "num_associated_deals": 1,
            "hs_email_domain": "eclat.co",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000005"),
        hubspot_id="5821038",
        name="Kwame Asante",
        company="TradeRoute Logistics",
        email="kwame@traderoute.com",
        phone="+1 (713) 555-0378",
        role="SVP Operations",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=67000,
        inactive_days=201,
        last_activity_at=datetime(2025, 11, 9, tzinfo=timezone.utc),
        assigned_to_id=USER_JORDAN_ID,
        industry="Logistics",
        company_size="500-2000",
        location="Houston",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "NEW",
            "lifecyclestage": "lead",
            "createdate": "2025-05-30T07:45:00Z",
            "lastmodifieddate": "2025-11-09T16:00:00Z",
            "num_associated_deals": 0,
            "hs_email_domain": "traderoute.com",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000006"),
        hubspot_id="5821039",
        name="Jennifer Park",
        company="Luminary EdTech",
        email="j.park@luminaryedtech.com",
        phone="+1 (617) 555-0517",
        role="Director of Product",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=19000,
        inactive_days=77,
        last_activity_at=datetime(2026, 3, 13, tzinfo=timezone.utc),
        assigned_to_id=USER_SAM_ID,
        industry="EdTech",
        company_size="50-200",
        location="Boston",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "CONNECTED",
            "lifecyclestage": "lead",
            "createdate": "2025-12-01T11:30:00Z",
            "lastmodifieddate": "2026-03-13T09:45:00Z",
            "num_associated_deals": 0,
            "hs_email_domain": "luminaryedtech.com",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000007"),
        hubspot_id="5821040",
        name="Lucas Andrade",
        company="ShieldNet Security",
        email="l.andrade@shieldnet.io",
        phone="+1 (408) 555-0283",
        role="CISO",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=95000,
        inactive_days=55,
        last_activity_at=datetime(2026, 4, 4, tzinfo=timezone.utc),
        assigned_to_id=USER_ALEX_ID,
        industry="Cybersecurity",
        company_size="200-500",
        location="San Jose",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:opportunity"],
        meta={
            "hs_lead_status": "IN_PROGRESS",
            "lifecyclestage": "opportunity",
            "createdate": "2026-01-10T15:00:00Z",
            "lastmodifieddate": "2026-04-04T12:00:00Z",
            "num_associated_deals": 2,
            "hs_email_domain": "shieldnet.io",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000008"),
        hubspot_id="5821041",
        name="Anna Kovacs",
        company="PeopleFirst HR",
        email="anna.kovacs@peoplefirsthr.com",
        phone="+1 (312) 555-0145",
        role="VP People Operations",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=27000,
        inactive_days=88,
        last_activity_at=datetime(2026, 3, 2, tzinfo=timezone.utc),
        assigned_to_id=USER_JORDAN_ID,
        industry="HR Tech",
        company_size="100-500",
        location="Chicago",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "OPEN",
            "lifecyclestage": "lead",
            "createdate": "2025-10-18T10:00:00Z",
            "lastmodifieddate": "2026-03-02T14:30:00Z",
            "num_associated_deals": 1,
            "hs_email_domain": "peoplefirsthr.com",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000009"),
        hubspot_id="5821042",
        name="Kevin O'Brien",
        company="Altitude PropTech",
        email="k.obrien@altitudeproptech.com",
        phone="+1 (617) 555-0622",
        role="Co-Founder & CEO",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=44000,
        inactive_days=122,
        last_activity_at=datetime(2026, 1, 27, tzinfo=timezone.utc),
        assigned_to_id=USER_SAM_ID,
        industry="PropTech",
        company_size="10-50",
        location="Boston",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "BAD_TIMING",
            "lifecyclestage": "lead",
            "createdate": "2025-09-05T08:30:00Z",
            "lastmodifieddate": "2026-01-27T11:15:00Z",
            "num_associated_deals": 0,
            "hs_email_domain": "altitudeproptech.com",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000010"),
        hubspot_id="5821043",
        name="Fatima Al-Zahrawi",
        company="Lexora Legal AI",
        email="f.alzahrawi@lexora.ai",
        phone="+1 (202) 555-0839",
        role="Chief Legal Officer",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=58000,
        inactive_days=174,
        last_activity_at=datetime(2025, 12, 5, tzinfo=timezone.utc),
        assigned_to_id=USER_ALEX_ID,
        industry="LegalTech",
        company_size="50-200",
        location="Washington DC",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "NEW",
            "lifecyclestage": "lead",
            "createdate": "2025-06-12T09:00:00Z",
            "lastmodifieddate": "2025-12-05T17:45:00Z",
            "num_associated_deals": 0,
            "hs_email_domain": "lexora.ai",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000011"),
        hubspot_id="5821044",
        name="Raj Krishnamurthy",
        company="Datastream Platform",
        email="raj.k@datastream.io",
        phone="+1 (415) 555-0991",
        role="Head of Engineering",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=110000,
        inactive_days=98,
        last_activity_at=datetime(2026, 2, 20, tzinfo=timezone.utc),
        assigned_to_id=USER_JORDAN_ID,
        industry="Data Platform",
        company_size="200-500",
        location="San Francisco",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:opportunity"],
        meta={
            "hs_lead_status": "OPEN",
            "lifecyclestage": "opportunity",
            "createdate": "2025-10-01T12:00:00Z",
            "lastmodifieddate": "2026-02-20T10:30:00Z",
            "num_associated_deals": 1,
            "hs_email_domain": "datastream.io",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000012"),
        hubspot_id="5821045",
        name="Emily Thornton",
        company="Coverbase InsurTech",
        email="emily.thornton@coverbase.com",
        phone="+1 (646) 555-0267",
        role="VP of Sales",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=36000,
        inactive_days=65,
        last_activity_at=datetime(2026, 3, 25, tzinfo=timezone.utc),
        assigned_to_id=USER_SAM_ID,
        industry="InsurTech",
        company_size="100-500",
        location="New York",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "CONNECTED",
            "lifecyclestage": "lead",
            "createdate": "2025-11-20T14:00:00Z",
            "lastmodifieddate": "2026-03-25T09:00:00Z",
            "num_associated_deals": 1,
            "hs_email_domain": "coverbase.com",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000013"),
        hubspot_id="5821046",
        name="Daniel Kowalski",
        company="SupplyChain Pro",
        email="d.kowalski@supplychainpro.com",
        phone="+1 (312) 555-0713",
        role="Procurement Manager",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=23000,
        inactive_days=157,
        last_activity_at=datetime(2025, 12, 23, tzinfo=timezone.utc),
        assigned_to_id=USER_ALEX_ID,
        industry="Supply Chain",
        company_size="500-2000",
        location="Chicago",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "UNQUALIFIED",
            "lifecyclestage": "lead",
            "createdate": "2025-07-08T10:15:00Z",
            "lastmodifieddate": "2025-12-23T13:00:00Z",
            "num_associated_deals": 0,
            "hs_email_domain": "supplychainpro.com",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000014"),
        hubspot_id="5821047",
        name="Mei Lin Zhang",
        company="Pixel Commerce",
        email="meilin.zhang@pixelcommerce.cn",
        phone="+1 (650) 555-0384",
        role="Director of Marketing",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=48000,
        inactive_days=83,
        last_activity_at=datetime(2026, 3, 7, tzinfo=timezone.utc),
        assigned_to_id=USER_JORDAN_ID,
        industry="Marketing Tech",
        company_size="50-200",
        location="Palo Alto",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "IN_PROGRESS",
            "lifecyclestage": "lead",
            "createdate": "2025-12-15T08:00:00Z",
            "lastmodifieddate": "2026-03-07T16:45:00Z",
            "num_associated_deals": 1,
            "hs_email_domain": "pixelcommerce.cn",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000015"),
        hubspot_id="5821048",
        name="Omar Suleiman",
        company="BuildSmart Construction",
        email="omar.s@buildsmart.co",
        phone="+1 (469) 555-0556",
        role="Operations VP",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=62000,
        inactive_days=219,
        last_activity_at=datetime(2025, 10, 22, tzinfo=timezone.utc),
        assigned_to_id=USER_SAM_ID,
        industry="Construction Tech",
        company_size="200-500",
        location="Dallas",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "NEW",
            "lifecyclestage": "lead",
            "createdate": "2025-04-18T11:20:00Z",
            "lastmodifieddate": "2025-10-22T14:00:00Z",
            "num_associated_deals": 0,
            "hs_email_domain": "buildsmart.co",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000016"),
        hubspot_id="5821049",
        name="Yuki Tanaka",
        company="Shopr E-commerce",
        email="yuki.tanaka@shopr.jp",
        phone="+1 (415) 555-0162",
        role="Product Lead",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=39000,
        inactive_days=71,
        last_activity_at=datetime(2026, 3, 19, tzinfo=timezone.utc),
        assigned_to_id=USER_ALEX_ID,
        industry="E-commerce",
        company_size="50-200",
        location="San Francisco",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "OPEN",
            "lifecyclestage": "lead",
            "createdate": "2026-01-07T09:30:00Z",
            "lastmodifieddate": "2026-03-19T11:50:00Z",
            "num_associated_deals": 1,
            "hs_email_domain": "shopr.jp",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000017"),
        hubspot_id="5821050",
        name="Alexandra Petrov",
        company="GenomIQ BioTech",
        email="a.petrov@genomiq.bio",
        phone="+1 (617) 555-0748",
        role="VP of Partnerships",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=130000,
        inactive_days=47,
        last_activity_at=datetime(2026, 4, 12, tzinfo=timezone.utc),
        assigned_to_id=USER_JORDAN_ID,
        industry="BioTech",
        company_size="100-500",
        location="Cambridge",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:opportunity"],
        meta={
            "hs_lead_status": "IN_PROGRESS",
            "lifecyclestage": "opportunity",
            "createdate": "2026-02-01T13:00:00Z",
            "lastmodifieddate": "2026-04-12T10:15:00Z",
            "num_associated_deals": 1,
            "hs_email_domain": "genomiq.bio",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000018"),
        hubspot_id="5821051",
        name="Marcus Johnson",
        company="Nexwave Telecom",
        email="m.johnson@nexwave.net",
        phone="+1 (972) 555-0493",
        role="Director of Technology",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=52000,
        inactive_days=136,
        last_activity_at=datetime(2026, 1, 13, tzinfo=timezone.utc),
        assigned_to_id=USER_SAM_ID,
        industry="Telecom Tech",
        company_size="500-2000",
        location="Dallas",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "BAD_TIMING",
            "lifecyclestage": "lead",
            "createdate": "2025-08-25T07:00:00Z",
            "lastmodifieddate": "2026-01-13T15:20:00Z",
            "num_associated_deals": 0,
            "hs_email_domain": "nexwave.net",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000019"),
        hubspot_id="5821052",
        name="Aisha Mohammed",
        company="GreenGrid ClimaTech",
        email="aisha.m@greengrid.earth",
        phone="+1 (720) 555-0617",
        role="Head of Sales",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=71000,
        inactive_days=59,
        last_activity_at=datetime(2026, 3, 31, tzinfo=timezone.utc),
        assigned_to_id=USER_ALEX_ID,
        industry="Climate Tech",
        company_size="50-200",
        location="Denver",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:lead"],
        meta={
            "hs_lead_status": "CONNECTED",
            "lifecyclestage": "lead",
            "createdate": "2026-01-15T12:30:00Z",
            "lastmodifieddate": "2026-03-31T09:00:00Z",
            "num_associated_deals": 1,
            "hs_email_domain": "greengrid.earth",
        },
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-c000-000000000020"),
        hubspot_id="5821053",
        name="Thomas Bergmann",
        company="AutoIQ Automotive",
        email="t.bergmann@autoiq.de",
        phone="+1 (313) 555-0824",
        role="Chief Revenue Officer",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=87000,
        inactive_days=112,
        last_activity_at=datetime(2026, 2, 6, tzinfo=timezone.utc),
        assigned_to_id=USER_JORDAN_ID,
        industry="Automotive Tech",
        company_size="200-500",
        location="Detroit",
        source="hubspot",
        tags=["hubspot", "lifecyclestage:opportunity"],
        meta={
            "hs_lead_status": "OPEN",
            "lifecyclestage": "opportunity",
            "createdate": "2025-09-30T10:00:00Z",
            "lastmodifieddate": "2026-02-06T13:45:00Z",
            "num_associated_deals": 1,
            "hs_email_domain": "autoiq.de",
        },
    ),
]

LEADS = [
    dict(
        id=uuid.UUID("00000000-0000-4000-b000-000000000001"),
        name="Sarah Chen",
        company="TechFlow Solutions",
        email="sarah.chen@techflow.io",
        phone="+1 (415) 555-0182",
        role="VP of Engineering",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=48000,
        inactive_days=67,
        last_activity_at=datetime(2026, 3, 19, tzinfo=timezone.utc),
        assigned_to_id=USER_ALEX_ID,
        industry="SaaS",
        company_size="200-500",
        location="San Francisco, CA",
        source="HubSpot",
        tags=["enterprise", "high-value", "technical"],
        meta={"assigned_to_name": "Alex Rivera", "campaigns": ["campaign-001"]},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-b000-000000000002"),
        name="Marcus Williams",
        company="GrowthBase Inc",
        email="marcus@growthbase.com",
        phone="+1 (312) 555-0241",
        role="CEO",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=32000,
        inactive_days=45,
        last_activity_at=datetime(2026, 4, 10, tzinfo=timezone.utc),
        assigned_to_id=USER_JORDAN_ID,
        industry="Marketing Tech",
        company_size="50-200",
        location="Chicago, IL",
        source="HubSpot",
        tags=["startup", "high-intent"],
        meta={"assigned_to_name": "Jordan Kim", "campaigns": ["campaign-002"]},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-b000-000000000003"),
        name="Priya Patel",
        company="Meridian Analytics",
        email="priya.patel@meridian.ai",
        phone="+1 (212) 555-0309",
        role="Head of RevOps",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=75000,
        inactive_days=112,
        last_activity_at=datetime(2026, 2, 3, tzinfo=timezone.utc),
        assigned_to_id=USER_ALEX_ID,
        industry="Analytics",
        company_size="500-2000",
        location="New York, NY",
        source="HubSpot",
        tags=["enterprise", "revops", "high-value"],
        meta={"assigned_to_name": "Alex Rivera", "campaigns": []},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-b000-000000000004"),
        name="David Okafor",
        company="Nexus Capital Partners",
        email="d.okafor@nexuscap.com",
        phone="+1 (310) 555-0127",
        role="Managing Director",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=120000,
        inactive_days=89,
        last_activity_at=datetime(2026, 2, 25, tzinfo=timezone.utc),
        assigned_to_id=USER_JORDAN_ID,
        industry="Finance",
        company_size="50-200",
        location="Los Angeles, CA",
        source="HubSpot",
        tags=["financial", "enterprise", "warm"],
        meta={"assigned_to_name": "Jordan Kim", "campaigns": ["campaign-001"]},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-b000-000000000005"),
        name="Elena Rodriguez",
        company="CloudFirst Systems",
        email="elena.r@cloudfirst.com",
        phone="+1 (512) 555-0398",
        role="CTO",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=28000,
        inactive_days=53,
        last_activity_at=datetime(2026, 4, 2, tzinfo=timezone.utc),
        assigned_to_id=USER_SAM_ID,
        industry="Cloud Infrastructure",
        company_size="100-500",
        location="Austin, TX",
        source="HubSpot",
        tags=["cloud", "technical", "mid-market"],
        meta={"assigned_to_name": "Sam Torres", "campaigns": ["campaign-003"]},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-b000-000000000006"),
        name="James Liu",
        company="Quantum Retail Co.",
        email="j.liu@quantumretail.com",
        phone="+1 (617) 555-0215",
        role="Director of Technology",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.REACTIVATED,
        confidence=0.0,
        deal_value=55000,
        inactive_days=30,
        last_activity_at=datetime(2026, 4, 25, tzinfo=timezone.utc),
        assigned_to_id=USER_ALEX_ID,
        industry="Retail Tech",
        company_size="200-500",
        location="Boston, MA",
        source="HubSpot",
        tags=["retail", "integration-heavy"],
        meta={"assigned_to_name": "Alex Rivera", "campaigns": ["campaign-002", "campaign-004"]},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-b000-000000000007"),
        name="Amara Nwosu",
        company="Pinnacle Health AI",
        email="amara@pinnaclehealth.ai",
        phone="+1 (415) 555-0467",
        role="VP of Product",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.MEETING_BOOKED,
        confidence=0.0,
        deal_value=92000,
        inactive_days=0,
        last_activity_at=datetime(2026, 5, 23, tzinfo=timezone.utc),
        assigned_to_id=USER_JORDAN_ID,
        industry="Health Tech",
        company_size="100-500",
        location="San Francisco, CA",
        source="HubSpot",
        tags=["health-tech", "high-value", "hot"],
        meta={"assigned_to_name": "Jordan Kim", "campaigns": ["campaign-001"]},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-b000-000000000008"),
        name="Tyler Brennan",
        company="Forge Manufacturing",
        email="tyler.brennan@forge-mfg.com",
        phone="+1 (216) 555-0334",
        role="Operations Director",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=38000,
        inactive_days=78,
        last_activity_at=datetime(2026, 3, 7, tzinfo=timezone.utc),
        assigned_to_id=USER_SAM_ID,
        industry="Manufacturing",
        company_size="500-2000",
        location="Cleveland, OH",
        source="HubSpot",
        tags=["manufacturing", "needs-champion"],
        meta={"assigned_to_name": "Sam Torres", "campaigns": []},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-b000-000000000009"),
        name="Natasha Ivanova",
        company="DataSphere Analytics",
        email="n.ivanova@datasphere.io",
        phone="+1 (206) 555-0289",
        role="Chief Data Officer",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=64000,
        inactive_days=42,
        last_activity_at=datetime(2026, 4, 13, tzinfo=timezone.utc),
        assigned_to_id=USER_ALEX_ID,
        industry="Data Analytics",
        company_size="200-500",
        location="Seattle, WA",
        source="HubSpot",
        tags=["data", "enterprise", "evaluating"],
        meta={"assigned_to_name": "Alex Rivera", "campaigns": ["campaign-004"]},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-b000-000000000010"),
        name="Carlos Mendez",
        company="Vantage Logistics",
        email="c.mendez@vantagelogistics.com",
        phone="+1 (713) 555-0156",
        role="COO",
        segment=LeadSegment.UNKNOWN,
        status=LeadStatus.DORMANT,
        confidence=0.0,
        deal_value=85000,
        inactive_days=134,
        last_activity_at=datetime(2026, 1, 11, tzinfo=timezone.utc),
        assigned_to_id=USER_JORDAN_ID,
        industry="Logistics",
        company_size="500-2000",
        location="Houston, TX",
        source="HubSpot",
        tags=["logistics", "enterprise", "cold"],
        meta={"assigned_to_name": "Jordan Kim", "campaigns": []},
    ),
]


# Raw CRM engagement history — no sentiment, no embedding (both assigned by AI at runtime).
# Activity content reflects realistic sales conversations; the classify_lead AI step
# determines segments from this text.
ACTIVITIES = [
    # ── Sarah Chen / TechFlow Solutions (b001) ──────────────────────────────
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000001"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000001"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Sarah,\n\n"
            "Congrats on TechFlow's recent growth to 200+ seats — that's a big milestone.\n\n"
            "I'm reaching out because we've been working with RevOps teams at similar scale and "
            "I think there could be a strong fit. We help sales teams consolidate outreach and "
            "reactivation workflows into one platform, which typically cuts manual follow-up "
            "time by around 40%.\n\n"
            "Would you be open to a 20-minute intro call this week or next?\n\n"
            "Best,\nAlex Rivera\nAmperatech"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000002"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000001"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 2, 10, 14, 30, tzinfo=timezone.utc),
        summary=None,
        content=(
            "45-min call with Sarah. She's evaluating tools for their RevOps overhaul. "
            "Liked the workflow automation demo. Asked multiple times about per-seat vs. flat annual pricing "
            "and whether we offer startup discounts. Current tool contract ends March 31."
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000003"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000001"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Sarah,\n\n"
            "Great speaking with you last month. As discussed, I've put together the formal "
            "proposal.\n\n"
            "The platform at your scale (up to 300 seats) comes to $48,000/year, billed "
            "annually. This includes full workflow automation, CRM integrations, and a "
            "dedicated onboarding specialist for the first 90 days.\n\n"
            "I've attached the full proposal document. Happy to walk through it on a call "
            "or answer any questions from your CFO directly if that would help move "
            "things forward.\n\n"
            "Looking forward to hearing your thoughts.\n\n"
            "Best,\nAlex Rivera\nAmperatech"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000004"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000001"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 3, 19, 16, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Called Sarah to discuss alternatives. She's happy with the product but says finance "
            "won't approve a single annual invoice at this amount without a 90-day trial first. "
            "Escalated internally to see if we can offer a paid pilot structure. Deal on hold."
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),

    # ── Marcus Williams / GrowthBase Inc (b002) ─────────────────────────────
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000005"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000002"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 3, 1, 11, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "30-min intro call with Marcus. He's excited about the product and asked detailed "
            "questions about CRM integrations. Mentioned they're in the middle of a board "
            "fundraise and can't commit to new SaaS spend until Q3 planning is locked."
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000006"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000002"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 3, 20, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Sent a brief check-in. Marcus replied: 'Things are hectic here, fundraise is taking "
            "longer than expected. I'd love to revisit in May once we close the round and have "
            "budget visibility for H2.' Marked as nurture."
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000007"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000002"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 4, 10, 8, 30, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Marcus,\n\n"
            "Hope the fundraise is going well — I know Q1 can be intense.\n\n"
            "Just checking in to see if anything has shifted on your end regarding timing. "
            "No pressure at all — I just want to make sure we're still on your radar when "
            "budget visibility opens up for H2.\n\n"
            "Happy to set something up for May if that still works?\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),

    # ── Priya Patel / Meridian Analytics (b003) ─────────────────────────────
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000008"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000003"),
        type=ActivityType.CALL,
        occurred_at=datetime(2025, 10, 15, 13, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Priya is leading a formal vendor evaluation for a RevOps analytics platform. "
            "Three vendors shortlisted including us. She's thorough — sent a 12-item RFP the next day. "
            "Timeline: decision before end of Q4."
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000009"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000003"),
        type=ActivityType.MEETING,
        occurred_at=datetime(2025, 11, 20, 14, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "90-min demo with Priya and 4 of her team. Good engagement, lots of questions on "
            "data pipeline integrations and custom dashboards. Priya said we're their technical "
            "top pick but they're still weighing commercial terms against another vendor."
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000010"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000003"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2025, 12, 10, 9, 30, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Priya,\n\n"
            "Thanks for including us in your evaluation — it was great meeting your team.\n\n"
            "I've attached our full RFP responses along with a revised commercial proposal "
            "that reflects the scope we discussed. I've also included a side-by-side "
            "comparison of our implementation timeline vs. the other solutions you mentioned.\n\n"
            "I know you were targeting a decision by end of Q4 — are you still on track "
            "for that? Happy to schedule time with your team before the holidays if helpful.\n\n"
            "Best,\nAlex Rivera\nAmperatech"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000011"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000003"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 2, 3, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Priya called to let us know they've signed with a competing platform. She said the "
            "decision came down to existing contract relationships and the other vendor offered "
            "a bundled discount with tools already in their stack. She was complimentary about "
            "our product and said to stay in touch."
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),

    # ── David Okafor / Nexus Capital Partners (b004) ─────────────────────────
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000012"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000004"),
        type=ActivityType.CALL,
        occurred_at=datetime(2025, 12, 1, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Excellent 40-min call. David asked sharp questions about data security and compliance "
            "for financial services. Said he'd been burned by a vendor before and wanted to "
            "move carefully but quickly. Requested a proposal by end of week."
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000013"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000004"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2025, 12, 20, 11, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi David,\n\n"
            "Great connecting last week — I appreciate you being so direct about your "
            "requirements.\n\n"
            "As promised, I've put together the enterprise proposal. At $120,000/year, this "
            "covers your full team with enterprise-grade security controls, a dedicated CSM, "
            "and SLA guarantees. I've also attached our SOC 2 Type II report and Data "
            "Processing Agreement for your legal and compliance team to review.\n\n"
            "I know you mentioned wanting to move carefully but quickly — happy to get on "
            "a call with your COO whenever you're ready.\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000014"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000004"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi David,\n\n"
            "Just following up on the proposal I sent on December 20th.\n\n"
            "I hope you had a good break over the holidays. Wanted to check in and see if "
            "you and your COO had a chance to review the documents. Happy to schedule a "
            "call to walk through any questions, or adjust any of the commercial terms "
            "if needed.\n\n"
            "Let me know if there's a good time to reconnect.\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000015"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000004"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 2, 25, 15, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Tried email, phone, and LinkedIn over the past 6 weeks. Zero response from David "
            "or anyone else at Nexus Capital. His LinkedIn shows he's still active. "
            "Unclear if there was an internal decision or a personal change. Marking stale."
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),

    # ── Elena Rodriguez / CloudFirst Systems (b005) ──────────────────────────
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000016"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000005"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 2, 15, 15, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Good 35-min discovery. Elena is evaluating infrastructure tooling for a team of ~80. "
            "She likes the feature set but mentioned upfront that FY26 budget is already 90% "
            "allocated and any new spend needs strong ROI justification for the CFO."
        ),
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000017"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000005"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 3, 5, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Elena emailed to say their finance team froze all non-critical software spend "
            "for the rest of the fiscal year after a cloud cost overrun in Q1. She said she "
            "genuinely wants to proceed but can't get budget approved until FY27 planning in Q4."
        ),
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000018"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000005"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 4, 2, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Elena,\n\n"
            "Thanks for sharing the context around your FY26 budget constraints — I completely "
            "understand the position you're in.\n\n"
            "I've put together a one-page ROI summary tailored specifically to CloudFirst's "
            "team of 80, showing projected time savings and efficiency gains based on "
            "comparable implementations. My hope is this gives you something concrete to "
            "bring to your CFO when Q4 planning starts.\n\n"
            "No pressure to act now — I just want to make sure you have the right materials "
            "when the window opens.\n\n"
            "Best,\nSam Torres\nAmperatech"
        ),
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),

    # ── James Liu / Quantum Retail Co. (b006) ────────────────────────────────
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000019"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000006"),
        type=ActivityType.MEETING,
        occurred_at=datetime(2026, 1, 20, 13, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "60-min technical demo. James and two engineers were highly engaged with the "
            "automation and reporting features. They asked about webhook support and native "
            "integrations with Shopify Plus and their custom WMS."
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000020"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000006"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 2, 15, 11, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "James sent a detailed list of 4 integrations they need: Shopify Plus (we have), "
            "their custom WMS (we don't), Netsuite ERP (we don't), and a legacy EDI system. "
            "He said without at least the WMS connector, they can't move forward."
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000021"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000006"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Alex,\n\n"
            "Just saw your product update newsletter — nice work on the new features.\n\n"
            "Quick question: are the ERP connectors you mentioned actually coming in Q2? "
            "Specifically I'm wondering about NetSuite and WMS support. If those are confirmed "
            "for Q2, it would change our calculus significantly. The integration gaps were the "
            "main reason we put things on pause.\n\n"
            "Let me know.\n\n"
            "James"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000022"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000006"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 4, 25, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Alex,\n\n"
            "Hope things are going well on your end.\n\n"
            "We've hit a wall with our current reporting tool and I've been thinking about "
            "your platform again. The analytics limitations we're running into are exactly "
            "what you showed us in the demo.\n\n"
            "Two questions: first, any update on the WMS integration timeline? And second, "
            "is the pricing we discussed in March still current?\n\n"
            "Worth jumping on a call next week if you're available.\n\n"
            "James"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),

    # ── Amara Nwosu / Pinnacle Health AI (b007) ──────────────────────────────
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000023"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000007"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 3, 1, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Amara,\n\n"
            "Congrats on Pinnacle Health AI's Series B — that's a significant milestone and "
            "the team clearly deserves it.\n\n"
            "I'm reaching out because post-funding growth typically puts real pressure on "
            "RevOps infrastructure, and we've helped several HealthTech companies navigate "
            "that exact transition. With your team scaling, it might be worth a quick "
            "conversation about how we can support your go-to-market motion.\n\n"
            "Would you be open to a 20-minute call in the next week or two?\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000024"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000007"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 3, 15, 14, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Excellent 45-min call. Amara wants to scale their SDR team from 5 to 20 by end of "
            "year and needs better tooling now. She asked about implementation timeline and "
            "said she can make a decision within 2 weeks if the demo goes well."
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000025"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000007"),
        type=ActivityType.MEETING,
        occurred_at=datetime(2026, 5, 1, 13, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "90-min demo with Amara and their new Head of Sales. Both were very engaged. "
            "They asked about onboarding support and dedicated CSM. Amara said she wants "
            "to bring in the CFO for the final commercial discussion."
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000026"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000007"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 5, 23, 17, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Amara confirmed a meeting next Thursday with herself, the CFO, and Head of Sales. "
            "She said they're planning to sign before June. Proposal is at $92,000/year."
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),

    # ── Tyler Brennan / Forge Manufacturing (b008) ───────────────────────────
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000027"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000008"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 1, 10, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Tyler,\n\n"
            "I came across Forge Manufacturing's recent expansion announcement and wanted "
            "to reach out.\n\n"
            "I work with Operations Directors at manufacturing companies to help streamline "
            "workflow automation and team coordination tooling. Given the operational "
            "complexity that comes with scaling a manufacturing floor, I thought it might "
            "be worth a conversation.\n\n"
            "Would you have 30 minutes this week or next to explore whether there's a fit?\n\n"
            "Best,\nSam Torres\nAmperatech"
        ),
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000028"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000008"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 2, 1, 11, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Tyler is enthusiastic but confirmed he doesn't control the technology budget. "
            "That sits with the VP of Operations who is based in their Cleveland HQ. "
            "Tyler offered to introduce us but said his VP is 'hard to get in front of.'"
        ),
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000029"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000008"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 3, 7, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Tyler says he's brought it up internally twice but the VP of Ops is focused "
            "on a plant equipment upgrade and isn't taking meetings about software. "
            "Tyler can't push harder without overstepping. Deal is stalled at champion stage."
        ),
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),

    # ── Natasha Ivanova / DataSphere Analytics (b009) ────────────────────────
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000030"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000009"),
        type=ActivityType.MEETING,
        occurred_at=datetime(2026, 2, 15, 13, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Two-hour session with Natasha and 3 data engineers. They tested our API, "
            "asked about SLA guarantees, and ran sample queries against their staging data. "
            "Natasha said technically it's the best fit they've evaluated."
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000031"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000009"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Natasha,\n\n"
            "Great working through the technical evaluation with your team last month — "
            "it was clear you all did your homework.\n\n"
            "Following up with our pricing options:\n\n"
            "- Starter: $38,000/year (up to 50 users)\n"
            "- Professional: $64,000/year (up to 150 users) — best fit for your team\n"
            "- Enterprise: $95,000/year (unlimited users + dedicated support)\n\n"
            "Based on what you told me about your team size and requirements, Professional "
            "is the natural fit. Happy to explore whether we can work with your budget "
            "constraints — let's talk.\n\n"
            "Best,\nAlex Rivera\nAmperatech"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000032"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000009"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 4, 1, 14, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Natasha was direct: they can do $46k max and want a 2-year lock-in in exchange. "
            "She mentioned a competitor offered them a lower rate and she'd prefer us but "
            "can't justify the delta to her board without a concession."
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000033"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000009"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 4, 13, 16, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Escalated Natasha's request to sales leadership for a custom pricing exception. "
            "Natasha is waiting and said she has a board meeting mid-May where tooling budget "
            "will be finalized. Need a response before then or the window closes."
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),

    # ── Carlos Mendez / Vantage Logistics (b010) ─────────────────────────────
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000034"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000010"),
        type=ActivityType.CALL,
        occurred_at=datetime(2025, 9, 15, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "40-min call. Carlos had already researched the platform and had specific questions "
            "about fleet tracking integrations and API rate limits. Said he wants to consolidate "
            "3 current tools into one and has the budget approved for Q4."
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000035"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000010"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2025, 10, 20, 11, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Carlos,\n\n"
            "Really enjoyed our call last week — it's refreshing to talk with someone who's "
            "already done the research.\n\n"
            "As promised, I've attached the enterprise proposal. At $85,000/year, this includes "
            "your custom API volume limits (10M calls/month), a dedicated migration support "
            "package to consolidate your existing 3 tools, and a 90-day implementation "
            "guarantee.\n\n"
            "I'm confident this will give you the unified platform you're looking for. "
            "Happy to walk through the details with your team whenever works.\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000036"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000010"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2025, 11, 25, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Carlos,\n\n"
            "Just wanted to follow up on the proposal I sent a few weeks back.\n\n"
            "I know things can get busy — I just want to make sure the proposal landed "
            "and that you have everything you need to move forward. Happy to jump on a "
            "15-minute call to answer any questions from your team.\n\n"
            "Looking forward to hearing from you.\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000037"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-b000-000000000010"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 1, 11, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Tried email, phone, and LinkedIn message over 7 weeks. Zero response. "
            "His LinkedIn is active and he's posting. No internal intro contact available. "
            "Reason for going dark is unknown. Marking as dormant."
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id=None,
        embedding=None,
        meta={},
    ),

    # ── HubSpot leads — 2 activities each ────────────────────────────────────

    # Ryan Nakamura / Finlink Technologies (c001)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000038"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000001"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Ryan,\n\n"
            "I work with VP-level finance leaders at FinTech companies and noticed Finlink "
            "Technologies has been scaling quickly.\n\n"
            "We help RevOps and finance teams automate their outreach and reactivation "
            "workflows — the kind of repetitive follow-up that eats into your team's time. "
            "Worth a quick conversation?\n\n"
            "Best,\nAlex Rivera\nAmperatech"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821034_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000039"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000001"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 2, 24, 14, 0, tzinfo=timezone.utc),
        summary=None,
        content="Ryan responded to a follow-up saying Q1 is their busiest period and he'd circle back in April. No further contact since.",
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821034_002",
        embedding=None,
        meta={},
    ),

    # Isabella Torres / CareSync Health (c002)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000040"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000002"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc),
        summary=None,
        content="Isabella runs clinical operations across 12 sites. She liked the workflow automation features and asked about HIPAA compliance and audit logging. Good call, requested a product overview deck.",
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821035_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000041"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000002"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 3, 29, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Isabella,\n\n"
            "Great speaking with you last week — the clinical operations workflow challenges "
            "you described are exactly the kind of problems we solve.\n\n"
            "As promised, I've attached our product overview deck and our Business Associate "
            "Agreement template. The BAA covers HIPAA compliance requirements, and we also "
            "have our full security documentation available if your compliance officer "
            "needs it.\n\n"
            "Happy to set up a call with your compliance team whenever works.\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821035_002",
        embedding=None,
        meta={},
    ),

    # Mohammed Al-Hassan / Atlas Precision Manufacturing (c003)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000042"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000003"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2025, 11, 1, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Mohammed,\n\n"
            "I've been following Atlas Precision Manufacturing's growth and wanted to "
            "reach out.\n\n"
            "We work with Plant Directors at large-scale manufacturers to help streamline "
            "operations workflows and improve cross-team visibility. Given the complexity "
            "of running a multi-facility operation, I thought it might be worth a "
            "quick conversation.\n\n"
            "Would you have 30 minutes for a brief intro call?\n\n"
            "Best,\nSam Torres\nAmperatech"
        ),
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id="hs_eng_5821036_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000043"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000003"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 1, 6, 12, 0, tzinfo=timezone.utc),
        summary=None,
        content="After two follow-ups, Mohammed replied saying Atlas is in the middle of a major plant expansion project that absorbs all discretionary budget and management attention through Q3. He asked to be contacted in September.",
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id="hs_eng_5821036_002",
        embedding=None,
        meta={},
    ),

    # Sophie Dubois / Éclat Commerce (c004)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000044"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000004"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2025, 12, 1, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Bonjour Sophie,\n\n"
            "I came across Éclat Commerce's recent expansion into new European markets and "
            "wanted to reach out.\n\n"
            "We help digital commerce leaders automate and scale their sales and partnership "
            "workflows. Given your growth trajectory, I thought it might be worth a brief "
            "conversation to explore whether there's a fit.\n\n"
            "Would you be open to a 20-minute intro call?\n\n"
            "Best,\nAlex Rivera\nAmperatech"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821037_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000045"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000004"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 2, 9, 14, 0, tzinfo=timezone.utc),
        summary=None,
        content="Good 30-min call. Sophie is the champion but said any new vendor requires sign-off from their Paris HQ, which takes 60-90 days minimum. She said she'd submit an internal brief but couldn't commit to a timeline.",
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821037_002",
        embedding=None,
        meta={},
    ),

    # Kwame Asante / TradeRoute Logistics (c005)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000046"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000005"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2025, 10, 1, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Kwame,\n\n"
            "I work with logistics and supply chain leaders on operations automation and "
            "wanted to reach out to TradeRoute Logistics.\n\n"
            "We help ops teams eliminate manual coordination overhead across high-volume "
            "routing and dispatch workflows. Based on TradeRoute's scale, I thought this "
            "might be relevant.\n\n"
            "Open to a brief intro call this week?\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821038_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000047"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000005"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2025, 11, 9, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content="Three emails and two LinkedIn messages over 5 weeks with no response. Kwame is active on LinkedIn. Sending one final email before marking inactive.",
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821038_002",
        embedding=None,
        meta={},
    ),

    # Jennifer Park / Luminary EdTech (c006)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000048"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000006"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 2, 20, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content="Jennifer is evaluating product management tooling. She liked our roadmap and collaboration features. Mentioned they're a seed-stage company and every dollar is scrutinized by the board.",
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id="hs_eng_5821039_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000049"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000006"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 3, 13, 11, 0, tzinfo=timezone.utc),
        summary=None,
        content="Jennifer emailed to say they reviewed internally and have no allocated budget for new software this academic semester. She said she'd revisit during their annual planning in September.",
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id="hs_eng_5821039_002",
        embedding=None,
        meta={},
    ),

    # Lucas Andrade / ShieldNet Security (c007)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000050"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000007"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 3, 1, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Lucas,\n\n"
            "I wanted to reach out after reading about ShieldNet Security's recent expansion "
            "into enterprise threat detection.\n\n"
            "We work with CISOs and security operations leaders to help coordinate incident "
            "response workflows and vendor management at scale. As your team grows, tooling "
            "becomes critical — and I thought it was worth a conversation.\n\n"
            "Would you be open to a demo with your security engineering team?\n\n"
            "Best,\nAlex Rivera\nAmperatech"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821040_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000051"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000007"),
        type=ActivityType.MEETING,
        occurred_at=datetime(2026, 4, 4, 13, 0, tzinfo=timezone.utc),
        summary=None,
        content="90-min technical demo with Lucas and 5 security engineers. They ran penetration test scenarios and asked detailed questions about SOC 2, data residency, and incident response integrations. Lucas said this is the strongest fit they've seen. Proposal requested.",
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821040_002",
        embedding=None,
        meta={},
    ),

    # Anna Kovacs / PeopleFirst HR (c008)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000052"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000008"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 2, 1, 11, 0, tzinfo=timezone.utc),
        summary=None,
        content="Anna is consolidating their HR and people ops tools. She's evaluating 3 platforms and ours came up in a peer recommendation. Good alignment on features; she asked to see case studies from similar-sized companies.",
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821041_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000053"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000008"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 3, 2, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Anna,\n\n"
            "Thanks for the great conversation last month.\n\n"
            "As you requested, I've attached three case studies from HR Tech companies at "
            "similar scale to PeopleFirst — all showing measurable improvements in "
            "onboarding and people ops efficiency. I've also included a pricing summary "
            "for the platform tier that fits your team size.\n\n"
            "Happy to discuss further or set up a call with your team whenever "
            "is convenient.\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821041_002",
        embedding=None,
        meta={},
    ),

    # Kevin O'Brien / Altitude PropTech (c009)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000054"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000009"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2025, 11, 15, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Kevin,\n\n"
            "Saw the traction Altitude PropTech has been getting — impressive early momentum.\n\n"
            "I work with early-stage PropTech founders on sales automation and outreach "
            "tooling. As you start building your revenue motion, having the right "
            "infrastructure early can make a big difference. I'd love to show you how "
            "a few teams at your stage are using us.\n\n"
            "Worth a quick call whenever you come up for air?\n\n"
            "Best,\nSam Torres\nAmperatech"
        ),
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id="hs_eng_5821042_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000055"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000009"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 1, 27, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content="Followed up in January. Kevin replied saying Q1 is locked with fundraising activities and they're not onboarding any new tools. He asked to reconnect in April or May.",
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id="hs_eng_5821042_002",
        embedding=None,
        meta={},
    ),

    # Fatima Al-Zahrawi / Lexora Legal AI (c010)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000056"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000010"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2025, 9, 20, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Fatima,\n\n"
            "I've been following Lexora Legal AI's work on contract intelligence — "
            "really interesting space.\n\n"
            "I work with legal tech teams to help automate their business development "
            "and partner outreach workflows. As you scale your commercial motion, "
            "I thought it might be worth a brief conversation.\n\n"
            "Would you have 20 minutes for a quick intro call?\n\n"
            "Best,\nAlex Rivera\nAmperatech"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821043_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000057"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000010"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2025, 12, 5, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content="Three emails over 10 weeks with no reply. LinkedIn request ignored. Sending a final break-up email before archiving.",
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821043_002",
        embedding=None,
        meta={},
    ),

    # Raj Krishnamurthy / Datastream Platform (c011)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000058"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000011"),
        type=ActivityType.MEETING,
        occurred_at=datetime(2026, 1, 15, 13, 0, tzinfo=timezone.utc),
        summary=None,
        content="Two-hour session with Raj and 4 engineers. They tested the API and liked the real-time pipeline capabilities. Raj said they're actively budgeted for this purchase in Q1.",
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821044_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000059"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000011"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 2, 20, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Raj,\n\n"
            "Thanks again for including your engineering team in the demo session — the "
            "depth of questions made it clear your team knows what they're looking for.\n\n"
            "As requested, I've attached the full connector documentation for the data "
            "pipeline integrations we discussed. This covers our Kafka, Redshift, and "
            "custom webhook configurations with complete API reference.\n\n"
            "Let me know if your team has follow-up questions or needs anything else "
            "to complete the evaluation.\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821044_002",
        embedding=None,
        meta={},
    ),

    # Emily Thornton / Coverbase InsurTech (c012)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000060"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000012"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 2, 15, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content="Emily's team is trying to shorten sales cycles in a complex InsurTech B2B environment. Good alignment on use case. She asked about pipeline analytics and wanted to see an ROI model.",
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id="hs_eng_5821045_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000061"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000012"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 3, 25, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Emily,\n\n"
            "Really enjoyed our conversation last month — your team's focus on shortening "
            "sales cycles in InsurTech B2B is exactly the problem we solve.\n\n"
            "As promised, I've built out an ROI model tailored to a 15-person sales team "
            "like yours. Based on industry benchmarks and comparable customer data, the "
            "model shows an estimated 28% reduction in deal cycle time and approximately "
            "$180K in recovered pipeline per year.\n\n"
            "Happy to walk through the model with you and your VP of Revenue whenever "
            "is good.\n\n"
            "Best,\nSam Torres\nAmperatech"
        ),
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id="hs_eng_5821045_002",
        embedding=None,
        meta={},
    ),

    # Daniel Kowalski / SupplyChain Pro (c013)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000062"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000013"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2025, 10, 1, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Daniel,\n\n"
            "I came across SupplyChain Pro while researching procurement automation tools "
            "in your space.\n\n"
            "We've been working with procurement and supply chain operations leaders to "
            "help automate vendor onboarding, approval workflows, and contract renewal "
            "cycles. I think there could be a strong fit — would love to show you "
            "what we've built.\n\n"
            "Open to a 30-minute call this week or next?\n\n"
            "Best,\nAlex Rivera\nAmperatech"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821046_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000063"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000013"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2025, 12, 23, 11, 0, tzinfo=timezone.utc),
        summary=None,
        content="Daniel emailed to say their procurement committee has a standing policy of not onboarding new vendors in Q4 due to year-end audits. He said to reach back out in February.",
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821046_002",
        embedding=None,
        meta={},
    ),

    # Mei Lin Zhang / Pixel Commerce (c014)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000064"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000014"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 2, 10, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content="Mei Lin is running a formal evaluation of 4 marketing automation platforms. She's the DM and has budget authority. Good conversation, she asked for a competitive comparison.",
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821047_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000065"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000014"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 3, 7, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Mei Lin,\n\n"
            "Thanks for the thorough conversation — it's clear you're running a rigorous "
            "evaluation process, which I respect.\n\n"
            "As requested, I've attached a detailed comparison across the four platforms "
            "you're evaluating. I've tried to be as objective as possible while highlighting "
            "the areas where I believe we differentiate, particularly on workflow automation "
            "depth and integration flexibility.\n\n"
            "Happy to discuss any of the comparison points on a call.\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821047_002",
        embedding=None,
        meta={},
    ),

    # Omar Suleiman / BuildSmart Construction (c015)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000066"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000015"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2025, 8, 1, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Omar,\n\n"
            "I've been following BuildSmart Construction's project portfolio — the scale "
            "of what your team is executing is impressive.\n\n"
            "I work with Operations Directors at construction companies to help streamline "
            "project workflow coordination and subcontractor communications. Given the "
            "operational complexity of large-scale construction management, I thought "
            "it might be worth a quick conversation.\n\n"
            "Would you have 30 minutes this week?\n\n"
            "Best,\nSam Torres\nAmperatech"
        ),
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id="hs_eng_5821048_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000067"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000015"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2025, 10, 22, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content="Four outreach attempts across email and phone over 10 weeks. No response from Omar or anyone at BuildSmart. Company appears to be heads-down on a large government contract based on LinkedIn activity.",
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id="hs_eng_5821048_002",
        embedding=None,
        meta={},
    ),

    # Yuki Tanaka / Shopr E-commerce (c016)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000068"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000016"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 2, 15, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content="Yuki leads product for a fast-growing D2C brand. She's evaluating tooling to automate their post-purchase flows and CRM sync. Good fit on use case; she asked specifically about Shopify and Klaviyo integrations.",
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821049_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000069"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000016"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 3, 19, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Yuki,\n\n"
            "Great call last week — the post-purchase automation use case you described "
            "is a really strong fit for what we've built.\n\n"
            "As promised, I've attached our Shopify and Klaviyo integration guide. "
            "This covers the full setup process, data sync configuration, and the "
            "automation triggers your engineering lead will need to review.\n\n"
            "Let me know if you'd like to jump on a technical call with our integration "
            "team to answer any questions.\n\n"
            "Best,\nAlex Rivera\nAmperatech"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821049_002",
        embedding=None,
        meta={},
    ),

    # Alexandra Petrov / GenomIQ BioTech (c017)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000070"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000017"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 2, 15, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Alexandra,\n\n"
            "Congratulations on the new pharma partnership announcement — that's a "
            "significant validation of GenomIQ's platform.\n\n"
            "I'm reaching out because rapid BD growth at biotech companies typically "
            "creates real strain on partnership operations and deal coordination. "
            "We've helped similar teams at Series B/C stage build the infrastructure "
            "to manage multiple partnership tracks without dropping balls.\n\n"
            "Would you be open to a demo to see if there's a fit?\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821050_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000071"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000017"),
        type=ActivityType.MEETING,
        occurred_at=datetime(2026, 4, 12, 13, 0, tzinfo=timezone.utc),
        summary=None,
        content="90-min demo with Alexandra and GenomIQ's CEO. Both were highly engaged. CEO asked about data privacy for genomics data and multi-region deployment. Alexandra said they want to move fast — proposal requested by end of week.",
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821050_002",
        embedding=None,
        meta={},
    ),

    # Marcus Johnson / Nexwave Telecom (c018)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000072"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000018"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2025, 11, 1, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Marcus,\n\n"
            "I came across Nexwave Telecom while looking at network operations tooling "
            "in the enterprise telecom space.\n\n"
            "We work with ops leaders at telecom companies to help automate network "
            "operations coordination, incident workflows, and vendor management. "
            "Given Nexwave's scale, I thought it might be worth a conversation.\n\n"
            "Do you have 30 minutes for a brief intro call?\n\n"
            "Best,\nSam Torres\nAmperatech"
        ),
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id="hs_eng_5821051_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000073"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000018"),
        type=ActivityType.NOTE,
        occurred_at=datetime(2026, 1, 13, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content="Follow-up call with Marcus. He said their migration to a new core network OS is consuming all engineering and ops bandwidth through Q2. He explicitly asked to reconnect in July.",
        sentiment=None,
        author="Sam Torres",
        hubspot_engagement_id="hs_eng_5821051_002",
        embedding=None,
        meta={},
    ),

    # Aisha Mohammed / GreenGrid ClimaTech (c019)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000074"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000019"),
        type=ActivityType.CALL,
        occurred_at=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
        summary=None,
        content="Excellent 40-min call. Aisha heads sales for a fast-growing climate tech company and is actively looking for tools to scale their outbound motion. She asked for a proposal covering her 8-person team.",
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821052_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000075"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000019"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 3, 31, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Aisha,\n\n"
            "Really enjoyed our conversation last week — the momentum you're building "
            "at GreenGrid is impressive.\n\n"
            "Following up with the proposal we discussed. For your 8-person sales team, "
            "the platform comes to $71,000/year. This includes full outbound automation, "
            "CRM integration, and a dedicated onboarding specialist to get your team "
            "productive quickly.\n\n"
            "I know you mentioned presenting to your CEO at the next weekly — let me "
            "know if there's anything I can add to make that conversation easier.\n\n"
            "Best,\nAlex Rivera\nAmperatech"
        ),
        sentiment=None,
        author="Alex Rivera",
        hubspot_engagement_id="hs_eng_5821052_002",
        embedding=None,
        meta={},
    ),

    # Thomas Bergmann / AutoIQ Automotive (c020)
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000076"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000020"),
        type=ActivityType.MEETING,
        occurred_at=datetime(2026, 1, 10, 13, 0, tzinfo=timezone.utc),
        summary=None,
        content="Two-hour demo with Thomas (CRO) and 3 regional sales directors. Strong interest in pipeline forecasting and deal intelligence features. Thomas said they're in active vendor selection and our platform is the front-runner.",
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821053_001",
        embedding=None,
        meta={},
    ),
    dict(
        id=uuid.UUID("00000000-0000-4000-d000-000000000077"),
        org_id=ORG_ID,
        lead_id=uuid.UUID("00000000-0000-4000-c000-000000000020"),
        type=ActivityType.EMAIL,
        occurred_at=datetime(2026, 2, 6, 9, 0, tzinfo=timezone.utc),
        summary=None,
        content=(
            "Hi Thomas,\n\n"
            "It was great meeting you and the regional directors last week — that was "
            "a very engaged group.\n\n"
            "As discussed, I've put together the enterprise proposal. At $87,000/year, "
            "this covers your full revenue team with advanced pipeline forecasting, "
            "deal intelligence features, and dedicated implementation support.\n\n"
            "I've submitted this to your team as requested. Please let me know if your "
            "procurement team in Munich needs additional documentation — I'm happy to "
            "provide references, security certifications, or anything else they need.\n\n"
            "Best,\nJordan Kim\nAmperatech"
        ),
        sentiment=None,
        author="Jordan Kim",
        hubspot_engagement_id="hs_eng_5821053_002",
        embedding=None,
        meta={},
    ),
]


async def _upsert(db: AsyncSession, model_class, obj):
    """Insert obj or skip if primary key already exists."""
    existing = await db.get(model_class, obj.id)
    if existing is None:
        db.add(obj)
        return True
    return False


async def _generate_lead_crm_summaries(db: AsyncSession) -> int:
    """Generate AI CRM summaries for all leads from their activity history."""
    result = await db.execute(select(Lead))
    leads = result.scalars().all()
    count = 0
    for lead in leads:
        activities_result = await db.execute(
            select(CRMActivity)
            .where(CRMActivity.lead_id == lead.id)
            .order_by(CRMActivity.occurred_at)
        )
        activities = activities_result.scalars().all()
        if activities:
            lead.crm_summary = await generate_lead_crm_summary(activities)
            count += 1
    await db.flush()
    return count


async def _generate_activity_summaries(db: AsyncSession) -> int:
    """Generate AI summaries for all activities that have none."""
    result = await db.execute(
        select(CRMActivity).where(
            or_(
                CRMActivity.summary.is_(None),
                CRMActivity.type == ActivityType.EMAIL,
            )
        )
    )
    activities = result.scalars().all()
    count = 0
    for activity in activities:
        if activity.content:
            activity.summary = await generate_activity_summary(
                activity.type.value, activity.content
            )
            count += 1
    await db.flush()
    return count


async def _embed_all_activities(db: AsyncSession) -> int:
    """Generate embeddings for all activities. Must run after summaries are generated."""
    result = await db.execute(select(CRMActivity.id))
    activity_ids = result.scalars().all()
    if not activity_ids:
        return 0
    svc = EmbeddingService(db)
    embeddings = await svc.embed_activities_batch(activity_ids)
    return len(embeddings)


async def seed():
    settings = get_settings()
    factory = get_session_factory()

    async with factory() as db:
        # Organization
        org = Organization(
            id=ORG_ID,
            name="Amperatech",
            slug="amperatech",
            plan="enterprise",
        )
        created = await _upsert(db, Organization, org)

        # Admin user (with dev API key)
        admin = User(
            id=ADMIN_USER_ID,
            org_id=ORG_ID,
            email="sharath.kumar@amperatech.ai",
            name="Sharath Kumar",
            role=UserRole.ADMIN,
            clerk_user_id=None,
            api_key_hash=DEV_API_KEY_HASH,
        )
        await _upsert(db, User, admin)

        # Sales rep users
        for uid, name, email in [
            (USER_ALEX_ID, "Alex Rivera", "alex.rivera@amperatech.ai"),
            (USER_JORDAN_ID, "Jordan Kim", "jordan.kim@amperatech.ai"),
            (USER_SAM_ID, "Sam Torres", "sam.torres@amperatech.ai"),
        ]:
            rep = User(
                id=uid,
                org_id=ORG_ID,
                email=email,
                name=name,
                role=UserRole.SDR,
                clerk_user_id=None,
            )
            await _upsert(db, User, rep)

        # Embedding version (check by name since id is auto-generated)
        existing_emb = await db.execute(
            select(EmbeddingVersion).where(EmbeddingVersion.name == "text-embedding-3-small-v1")
        )
        if existing_emb.scalar_one_or_none() is None:
            emb = EmbeddingVersion(
                name="text-embedding-3-small-v1",
                model_name=settings.EMBEDDING_MODEL,
                dimension=settings.EMBEDDING_DIMENSION,
                description="OpenAI text-embedding-3-small (1536 dims)",
                is_active=True,
            )
            db.add(emb)

        # Leads
        leads_created = 0
        for data in LEADS:
            lead = Lead(org_id=ORG_ID, **data)
            if await _upsert(db, Lead, lead):
                leads_created += 1

        # HubSpot-style leads (segment=UNKNOWN, hubspot_id populated, source="hubspot")
        hs_created = 0
        for data in HUBSPOT_LEADS:
            lead = Lead(org_id=ORG_ID, **data)
            if await _upsert(db, Lead, lead):
                hs_created += 1

        # Flush leads to DB within the transaction before inserting activities (FK dependency)
        await db.flush()

        # CRM Activities
        activities_created = 0
        for data in ACTIVITIES:
            activity = CRMActivity(**data)
            if await _upsert(db, CRMActivity, activity):
                activities_created += 1

        await db.commit()
        print(f"Seeded: org={org.slug}, admin={admin.email}")
        print(f"Seeded: {leads_created} sample leads, {hs_created} HubSpot leads")
        print(f"Seeded: {activities_created} CRM activities")

    # Generate AI summaries after the seed session is fully closed so db2 gets
    # a clean connection with full visibility of the committed seed data.
    async with factory() as db2:
        summaries_generated = await _generate_activity_summaries(db2)
        lead_summaries_generated = await _generate_lead_crm_summaries(db2)
        embeddings_generated = await _embed_all_activities(db2)
        await db2.commit()
    print(f"Generated summaries for {summaries_generated} activities")
    print(f"Generated CRM summaries for {lead_summaries_generated} leads")
    print(f"Generated embeddings for {embeddings_generated} activities")

    print(f"Dev API key: {DEV_API_KEY}")


if __name__ == "__main__":
    asyncio.run(seed())
