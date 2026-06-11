CODEX_IMPLEMENT_SPRINT_11_TRUST_ENGINE

Role:

You are the Primary Implementation Agent for P2PSuperBot.

Implement Sprint 11 exactly according to approved specifications.

Do not redesign business logic.

Do not implement future sprints.

⸻

PRE-READ REQUIREMENTS

Read in order:

1. PROJECT_STATUS_DASHBOARD.md
2. PROJECT_MEMORY.md
3. TRUST_VERIFICATION_MODEL.md
4. 10_PHASE1_MASTER_SPECIFICATION.md
5. 11_PHASE1_IMPLEMENTATION_ROADMAP.md
6. 14_CODEX_STARTUP_PROMPT.md

Review Sprint 1–10 implementation before starting.

⸻

SPRINT INFORMATION

Sprint:

Sprint 11

Trust Engine

Goal:

Create the central trust calculation engine.

⸻

BUSINESS OBJECTIVE

Trust Engine becomes:

Single Source Of Truth

for:

Trust Level

Trust Score

Badges

Verification Status

Risk Score

Visibility Rank

Community Rank

Future Reputation Score

⸻

DESIGN PRINCIPLE

No module may calculate trust independently.

All modules must use:

TrustEngine

⸻

DATABASE TABLES

Create:

trust_profiles

trust_events

risk_events

risk_profiles

badge_assignments

trust_history

⸻

Use existing:

users

user_profiles

credit_accounts

user_wallets

kyc_submissions

ekyc_submissions

review_cases

audit_logs

⸻

TRUST PROFILE

One record per user.

Fields:

user_id

trust_level

trust_score

risk_score

verification_status

visibility_rank

community_rank

updated_at

⸻

TRUST LEVELS

LEVEL_0

ANONYMOUS

⸻

LEVEL_1

REGISTERED

Score:

100

⸻

LEVEL_2

KYC_VERIFIED

Score:

300

⸻

LEVEL_3

EKYC_VERIFIED

Score:

500

⸻

LEVEL_4

WALLET_VERIFIED

Score:

700

⸻

LEVEL_5

BANK_VERIFIED

Score:

900

⸻

LEVEL_6

MERCHANT_VERIFIED

Score:

1200

⸻

TRUST SCORE ENGINE

Base Score:

REGISTERED

100

⸻

KYC

+200

⸻

EKYC

+200

⸻

WALLET

+200

⸻

BANK

+200

⸻

MERCHANT

+300

⸻

ACTIVITY SCORE

Separate from base score.

Sources:

Successful Transactions

Wallet Activity

Community Endorsements

Verified Relationships

Future Features

⸻

Maximum:

500

⸻

Trust Score:

Base Score + Activity Score

⸻

VERIFICATION STATUS

Supported:

REGISTERED

KYC_VERIFIED

EKYC_VERIFIED

WALLET_VERIFIED

BANK_VERIFIED

MERCHANT_VERIFIED

SUSPENDED

BANNED

⸻

BADGE ENGINE

Supported:

REGISTERED

KYC VERIFIED

EKYC VERIFIED

WALLET VERIFIED

BANK VERIFIED

MERCHANT VERIFIED

TRUSTED MEMBER

TOP MERCHANT

⸻

Badges generated automatically.

⸻

VISIBILITY RANK

Based on:

Trust Score

Verification Level

Risk Score

⸻

Values:

LOW

NORMAL

HIGH

PRIORITY

ELITE

⸻

Used later in:

Search

Marketplace

Community

⸻

COMMUNITY RANK

Values:

BRONZE

SILVER

GOLD

PLATINUM

DIAMOND

⸻

Mapping:

0-299

BRONZE

300-599

SILVER

600-899

GOLD

900-1199

PLATINUM

1200+

DIAMOND

⸻

RISK ENGINE

Separate from trust.

Range:

0-100

⸻

Higher Risk

=

Worse

⸻

RISK EVENTS

Supported:

FAILED_KYC

DUPLICATE_IDENTITY

DUPLICATE_WALLET

FRAUD_REPORT

SUSPICIOUS_ACTIVITY

REJECTED_VERIFICATION

MANUAL_FLAG

⸻

RISK SCORE EXAMPLES

FAILED_KYC

+5

⸻

DUPLICATE_IDENTITY

+25

⸻

DUPLICATE_WALLET

+20

⸻

FRAUD_REPORT

+10

⸻

MANUAL_FLAG

Configurable

⸻

RISK CLASSIFICATION

0-19

LOW

⸻

20-49

MEDIUM

⸻

50-79

HIGH

⸻

80+

CRITICAL

⸻

TRUST EVENTS

Supported:

USER_REGISTERED

KYC_APPROVED

EKYC_APPROVED

WALLET_VERIFIED

BANK_VERIFIED

MERCHANT_APPROVED

TRUST_UPGRADED

BADGE_ASSIGNED

⸻

EVENT DRIVEN DESIGN

Trust Engine reacts to:

Events

⸻

Examples:

KYC Approved

↓

Create Trust Event

↓

Recalculate Trust

↓

Assign Badge

↓

Store History

⸻

TRUST RECALCULATION

Create:

recalculate_trust(user_id)

⸻

Triggered by:

Registration

KYC

eKYC

Wallet

Bank

Merchant

Admin Override

⸻

BADGE ASSIGNMENT ENGINE

Create:

assign_badges(user_id)

⸻

Automatic.

No manual assignment.

Except SUPER_ADMIN override.

⸻

TRUST HISTORY

Store:

Previous Score

New Score

Reason

Source Event

Timestamp

⸻

Immutable.

Append-only.

⸻

TRUST PROFILE API

GET /api/v1/trust/profile

⸻

Response:

{
“trust_level”: “LEVEL_4”,
“trust_score”: 700,
“risk_score”: 5,
“community_rank”: “GOLD”,
“badges”: []
}

⸻

TRUST HISTORY API

GET /api/v1/trust/history

⸻

Paginated.

⸻

RISK PROFILE API

GET /api/v1/trust/risk

⸻

Owner only.

Admin access allowed.

⸻

BADGE API

GET /api/v1/trust/badges

⸻

Return active badges.

⸻

ADMIN TRUST API

POST /api/v1/admin/trust/recalculate

⸻

SUPER_ADMIN only.

⸻

Purpose:

Repair

Migration

Data Sync

⸻

SECURITY REQUIREMENTS

Trust Score:

Read Only

⸻

Risk Score:

Read Only

⸻

No user modification.

⸻

All changes:

Engine Driven

Or Admin Override

With Audit Trail

⸻

AUDIT EVENTS

TRUST_RECALCULATED

TRUST_LEVEL_CHANGED

RISK_SCORE_CHANGED

BADGE_ASSIGNED

BADGE_REMOVED

ADMIN_TRUST_OVERRIDE

⸻

FILES TO CREATE

backend/services/trust_engine.py

backend/services/risk_engine.py

backend/services/badge_engine.py

backend/api/v1/trust/routes.py

backend/schemas/trust.py

backend/repositories/trust_repository.py

⸻

FILES TO UPDATE

KYC Module

eKYC Module

Wallet Module

Admin Review Module

Replace direct trust updates.

Use Trust Engine events.

⸻

TESTING REQUIREMENTS

Create:

tests/unit/trust/

tests/integration/trust/

tests/security/trust/

⸻

Unit Tests:

Trust Calculation

Badge Assignment

Risk Calculation

Visibility Ranking

Community Ranking

⸻

Integration Tests:

KYC Approval

eKYC Approval

Wallet Verification

Trust Upgrade

Risk Events

⸻

Security Tests:

Score Tampering

Unauthorized Recalculation

Badge Manipulation

Risk Manipulation

⸻

ACCEPTANCE CRITERIA

✓ Trust Profile Works

✓ Trust Calculation Works

✓ Badge Assignment Works

✓ Risk Engine Works

✓ Community Rank Works

✓ Visibility Rank Works

✓ Trust History Works

✓ Audit Logs Created

✓ Tests Pass

⸻

VALIDATION COMMANDS

pytest tests/unit/trust -v

pytest tests/integration/trust -v

pytest tests/security/trust -v

pytest -v

All tests must pass.

⸻

DOCUMENTATION UPDATE

Update:

PROJECT_STATUS_DASHBOARD.md

Change:

Sprint 11

IN PROGRESS

↓

COMPLETED

Update progress percentage.

⸻

COMPLETION REPORT

Create:

SPRINT_11_COMPLETION_REPORT.md

Include:

Summary

Trust Architecture

Risk Engine Design

Badge Engine Design

Files Created

APIs Added

Tests Added

Known Issues

Phase 2 Readiness

⸻

GIT COMMIT

Create commit:

[Sprint-11]

Trust Engine Completed

Push to repository.

⸻

DEFINITION OF DONE

✓ Trust Engine Works

✓ Risk Engine Works

✓ Badge Engine Works

✓ Trust History Works

✓ APIs Work

✓ Audit Logs Created

✓ Tests Pass

✓ Dashboard Updated

✓ Completion Report Created

✓ Git Commit Created

Only then may Sprint 11 be marked COMPLETE.

END OF DOCUMENT