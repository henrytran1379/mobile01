CODEX_IMPLEMENT_SPRINT_6_KYC

Role:

You are the Primary Implementation Agent for P2PSuperBot.

Implement Sprint 6 exactly according to approved specifications.

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
6. 04_PROFILE_KYC_EKYC_FLOW.md
7. 06_ADMIN_REVIEW_FLOW.md
8. 08_API_SERVICE_DESIGN_PHASE1.md
9. 14_CODEX_STARTUP_PROMPT.md

Review Sprint 1–5 implementation before starting.

⸻

SPRINT INFORMATION

Sprint:

Sprint 6

KYC Module

Goal:

Implement complete manual KYC verification workflow.

⸻

BUSINESS OBJECTIVE

KYC provides:

Identity Verification

Document Validation

Trust Upgrade

Fraud Reduction

Community Confidence

⸻

TRUST MODEL INTEGRATION

Before KYC:

Level 1

REGISTERED

Trust Score:

100

⸻

After KYC Approved:

Level 2

KYC VERIFIED

Trust Score:

300

Badge:

KYC VERIFIED

⸻

DATABASE TABLES USED

Use:

users

user_profiles

user_documents

kyc_submissions

verification_reviews

audit_logs

trust_scores

⸻

KYC REQUIREMENTS

User must upload:

1. CCCD Front
2. CCCD Back
3. Selfie

All required.

⸻

SUPPORTED FILE TYPES

Images:

jpg

jpeg

png

webp

⸻

Maximum size:

10 MB per file

⸻

KYC STATUS

Supported:

DRAFT

SUBMITTED

UNDER_REVIEW

APPROVED

REJECTED

EXPIRED

⸻

KYC FLOW

User

↓

Upload Documents

↓

OCR Processing

↓

Create KYC Submission

↓

Admin Review

↓

Approve / Reject

↓

Trust Level Updated

⸻

OCR PROCESSING

Extract:

Full Name

CCCD Number

Date Of Birth

Gender

Nationality

Issue Date

Issue Place

Expiry Date

Address

⸻

Store:

Structured JSON

⸻

Confidence Score:

0 - 100

⸻

DOCUMENT STORAGE

Store:

Original File

Thumbnail

OCR Result

Metadata

Hash

⸻

Generate:

SHA256 Hash

For duplicate detection.

⸻

DUPLICATE DETECTION

Check:

CCCD Number

Document Hash

⸻

Flag:

POSSIBLE_DUPLICATE

For Admin Review.

⸻

API 1

Create KYC Submission

POST /api/v1/kyc/submit

⸻

Request:

multipart/form-data

front_image

back_image

selfie_image

⸻

Response:

{
“success”: true,
“submission_id”: “…”,
“status”: “SUBMITTED”
}

⸻

API 2

Get KYC Status

GET /api/v1/kyc/status

⸻

Response:

{
“status”: “UNDER_REVIEW”,
“submitted_at”: “…”,
“trust_level_after_approval”: “LEVEL_2”
}

⸻

API 3

Get OCR Result

GET /api/v1/kyc/ocr-preview

⸻

Only visible to owner.

⸻

Response:

{
“full_name”: “…”,
“cccd_number”: “…”,
“confidence”: 94
}

⸻

OCR VALIDATION

Minimum confidence:

80%

⸻

If lower:

Require manual review.

⸻

Flag:

LOW_CONFIDENCE

⸻

SELFIE VALIDATION

Phase 1:

Manual review only.

No biometric matching.

⸻

Future Phase:

Face Matching

Liveness Detection

⸻

ADMIN REVIEW QUEUE

Create review item.

Queue:

KYC_REVIEW

⸻

Admin sees:

Submission

Documents

OCR Result

Duplicate Flags

History

⸻

APPROVAL FLOW

When Approved:

Update:

verification_status

trust_level

trust_score

badge

⸻

Create:

KYC_VERIFIED event

⸻

Generate audit logs.

⸻

REJECTION FLOW

Admin must provide:

Reason

⸻

Examples:

Blurry Image

Invalid Document

Document Mismatch

Fake Document

Duplicate Identity

⸻

Store rejection reason.

⸻

SECURITY REQUIREMENTS

Only owner can view documents.

Admins require:

KYC_REVIEW permission.

⸻

All access logged.

⸻

Never expose:

Full CCCD publicly.

⸻

Mask:

079*****789

⸻

AUDIT EVENTS

KYC_SUBMITTED

KYC_OCR_COMPLETED

KYC_REVIEW_STARTED

KYC_APPROVED

KYC_REJECTED

KYC_DUPLICATE_FLAGGED

⸻

FILES TO CREATE

backend/services/kyc_service.py

backend/services/ocr_service.py

backend/api/v1/kyc/routes.py

backend/schemas/kyc.py

backend/repositories/kyc_repository.py

⸻

OCR LIBRARIES

Approved:

Tesseract OCR

EasyOCR

Equivalent open-source OCR

⸻

Design OCR provider abstraction.

⸻

TESTING REQUIREMENTS

Create:

tests/unit/kyc/

tests/integration/kyc/

tests/security/kyc/

⸻

Unit Tests:

OCR Parsing

Document Validation

Status Changes

Trust Upgrade Logic

Duplicate Detection

⸻

Integration Tests:

Submit KYC

OCR Processing

Admin Approval

Admin Rejection

Trust Score Update

⸻

Security Tests:

Unauthorized Access

Document Leakage

Permission Escalation

Direct File Access

⸻

ACCEPTANCE CRITERIA

✓ KYC Submission Works

✓ OCR Processing Works

✓ Duplicate Detection Works

✓ Admin Review Works

✓ Approval Works

✓ Rejection Works

✓ Trust Level Updated

✓ Trust Score Updated

✓ Audit Logs Created

✓ Unit Tests Pass

✓ Integration Tests Pass

✓ Security Tests Pass

⸻

VALIDATION COMMANDS

pytest tests/unit/kyc -v

pytest tests/integration/kyc -v

pytest tests/security/kyc -v

pytest -v

All tests must pass.

⸻

DOCUMENTATION UPDATE

Update:

PROJECT_STATUS_DASHBOARD.md

Change:

Sprint 6

IN PROGRESS

↓

COMPLETED

Update progress percentage.

⸻

COMPLETION REPORT

Create:

SPRINT_6_COMPLETION_REPORT.md

Include:

Summary

OCR Design

Duplicate Detection Design

Files Created

APIs Added

Tests Added

Trust Model Impact

Known Issues

Sprint 7 Readiness

⸻

GIT COMMIT

Create commit:

[Sprint-6]

KYC Module Completed

Push to repository.

⸻

DEFINITION OF DONE

✓ KYC Submission Works

✓ OCR Works

✓ Duplicate Detection Works

✓ Admin Review Works

✓ Trust Upgrade Works

✓ Audit Logs Created

✓ Tests Pass

✓ Dashboard Updated

✓ Completion Report Created

✓ Git Commit Created

Only then may Sprint 6 be marked COMPLETE.

END OF DOCUMENT