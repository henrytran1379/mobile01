CODEX_IMPLEMENT_SPRINT_10_ADMIN_REVIEW_SYSTEM

Role:

You are the Primary Implementation Agent for P2PSuperBot.

Implement Sprint 10 exactly according to approved specifications.

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
6. 06_ADMIN_REVIEW_FLOW.md
7. 14_CODEX_STARTUP_PROMPT.md

Review Sprint 1–9 implementation before starting.

⸻

SPRINT INFORMATION

Sprint:

Sprint 10

Admin Review System

Goal:

Build centralized verification review platform.

⸻

BUSINESS OBJECTIVE

All verification modules must use one review engine.

Modules:

KYC

eKYC

Wallet Verification

Future Bank Verification

Future Merchant Verification

Future Fraud Investigation

⸻

DESIGN PRINCIPLE

Single Review Center

Single Review Workflow

Single Audit Trail

Single Decision Engine

⸻

DATABASE TABLES

Create:

review_cases

review_case_events

review_assignments

review_comments

review_attachments

review_decisions

⸻

Use existing:

audit_logs

users

verification_reviews

kyc_submissions

ekyc_submissions

wallet_verifications

⸻

REVIEW CASE TYPES

Supported:

KYC

EKYC

WALLET

BANK

MERCHANT

FRAUD

MANUAL

⸻

REVIEW CASE STATUS

NEW

PENDING

ASSIGNED

UNDER_REVIEW

ESCALATED

APPROVED

REJECTED

CANCELLED

CLOSED

⸻

REVIEW PRIORITY

LOW

NORMAL

HIGH

URGENT

CRITICAL

⸻

REVIEW QUEUE

Create unified queue:

GET /api/v1/admin/reviews

⸻

Filters:

Type

Status

Priority

Assigned Reviewer

Date Range

User

Trust Level

⸻

Sorting:

Priority

Created Date

Assigned Reviewer

⸻

REVIEW CASE

Each case contains:

Case ID

Case Type

User

Trust Level

Submission Source

Evidence

Comments

History

Decision

Audit Trail

⸻

CASE CREATION

When:

KYC Submitted

↓

Create Review Case

⸻

When:

eKYC Submitted

↓

Create Review Case

⸻

When:

Wallet Verification Flagged

↓

Create Review Case

⸻

CASE ASSIGNMENT

Create API:

POST /api/v1/admin/reviews/{case_id}/assign

⸻

Request:

{
“reviewer_id”: “…”
}

⸻

Actions:

Assign

Reassign

Take Ownership

⸻

REVIEW COMMENTS

Create API:

POST /api/v1/admin/reviews/{case_id}/comments

⸻

Comment Types:

NOTE

REQUEST_INFO

ESCALATION

WARNING

INTERNAL

⸻

All comments timestamped.

⸻

REVIEW ATTACHMENTS

Support:

Images

PDF

JSON Evidence

Blockchain Evidence

⸻

Maximum:

50 MB

⸻

EVIDENCE VIEWER

Reviewer can view:

CCCD Front

CCCD Back

Selfie

eKYC PDF

OCR Result

Wallet Address

Transaction Hash

Verification History

Trust History

⸻

APPROVAL API

POST /api/v1/admin/reviews/{case_id}/approve

⸻

Requirements:

Reviewer Permission

⸻

Result:

Case Closed

Approval Event Created

Module Callback Executed

Trust Updated

Audit Log Created

⸻

REJECTION API

POST /api/v1/admin/reviews/{case_id}/reject

⸻

Request:

{
“reason”: “…”
}

⸻

Reason Required.

⸻

Result:

Case Closed

Rejection Event Created

Audit Log Created

⸻

ESCALATION API

POST /api/v1/admin/reviews/{case_id}/escalate

⸻

Request:

{
“reason”: “…”,
“target_role”: “SENIOR_REVIEWER”
}

⸻

Status:

ESCALATED

⸻

REVIEW DECISION ENGINE

Decision Types:

APPROVE

REJECT

REQUEST_INFORMATION

ESCALATE

CANCEL

⸻

Store:

Reviewer

Timestamp

Reason

Evidence Snapshot

⸻

REVIEW HISTORY

Every action creates:

Review Event

⸻

Examples:

CASE_CREATED

CASE_ASSIGNED

COMMENT_ADDED

ESCALATED

APPROVED

REJECTED

⸻

ADMIN ROLES

REVIEWER

SENIOR_REVIEWER

COMPLIANCE

ADMIN

SUPER_ADMIN

⸻

PERMISSION MATRIX

REVIEWER

Approve Standard Cases

⸻

SENIOR_REVIEWER

Approve Escalated Cases

⸻

COMPLIANCE

Fraud Investigation

⸻

SUPER_ADMIN

Override Any Decision

⸻

FRAUD FLAGS

Support:

DUPLICATE_IDENTITY

DUPLICATE_WALLET

FAKE_DOCUMENT

SUSPICIOUS_ACTIVITY

HIGH_RISK_USER

⸻

AUDIT REQUIREMENTS

Every action logged.

No deletion allowed.

Immutable history.

⸻

AUDIT EVENTS

CASE_CREATED

CASE_ASSIGNED

CASE_REASSIGNED

CASE_ESCALATED

CASE_APPROVED

CASE_REJECTED

COMMENT_ADDED

ATTACHMENT_ADDED

OVERRIDE_EXECUTED

⸻

DASHBOARD METRICS

Pending Cases

Average Review Time

Approval Rate

Rejection Rate

Escalation Rate

Reviewer Productivity

⸻

FILES TO CREATE

backend/services/review_service.py

backend/services/review_case_service.py

backend/api/v1/admin/reviews/routes.py

backend/schemas/review.py

backend/repositories/review_repository.py

⸻

FILES TO UPDATE

KYC Module

eKYC Module

Wallet Module

Replace direct approval logic with Review System.

⸻

TESTING REQUIREMENTS

Create:

tests/unit/reviews/

tests/integration/reviews/

tests/security/reviews/

⸻

Unit Tests:

Case Creation

Assignment

Comments

Escalation

Decision Engine

⸻

Integration Tests:

KYC Review

eKYC Review

Wallet Review

Approval Flow

Rejection Flow

⸻

Security Tests:

Unauthorized Approval

Reviewer Escalation Abuse

Comment Tampering

Audit Manipulation

Case Enumeration

⸻

ACCEPTANCE CRITERIA

✓ Unified Queue Works

✓ Assignment Works

✓ Comments Work

✓ Escalation Works

✓ Approval Works

✓ Rejection Works

✓ Audit Trail Works

✓ Metrics Work

✓ Tests Pass

⸻

VALIDATION COMMANDS

pytest tests/unit/reviews -v

pytest tests/integration/reviews -v

pytest tests/security/reviews -v

pytest -v

All tests must pass.

⸻

DOCUMENTATION UPDATE

Update:

PROJECT_STATUS_DASHBOARD.md

Change:

Sprint 10

IN PROGRESS

↓

COMPLETED

Update progress percentage.

⸻

COMPLETION REPORT

Create:

SPRINT_10_COMPLETION_REPORT.md

Include:

Summary

Review Architecture

Decision Engine Design

Case Lifecycle

Files Created

Tests Added

Metrics Design

Known Issues

Sprint 11 Readiness

⸻

GIT COMMIT

Create commit:

[Sprint-10]

Admin Review System Completed

Push to repository.

⸻

DEFINITION OF DONE

✓ Review Queue Works

✓ Assignment Works

✓ Escalation Works

✓ Approval Works

✓ Rejection Works

✓ Audit Trail Works

✓ Tests Pass

✓ Dashboard Updated

✓ Completion Report Created

✓ Git Commit Created

Only then may Sprint 10 be marked COMPLETE.

END OF DOCUMENT