CODEX_IMPLEMENT_SPRINT_7_EKYC

Role:

You are the Primary Implementation Agent for P2PSuperBot.

Implement Sprint 7 exactly according to approved specifications.

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

Review Sprint 1–6 implementation before starting.

⸻

SPRINT INFORMATION

Sprint:

Sprint 7

eKYC Module

Goal:

Implement complete eKYC verification workflow using third-party eKYC PDF reports.

⸻

BUSINESS OBJECTIVE

eKYC provides:

Higher Trust

Lower Fraud Risk

Automated Identity Verification

Verified Identity Evidence

Cross-Platform Trust

⸻

TRUST MODEL INTEGRATION

Before eKYC:

Level 2

KYC VERIFIED

Trust Score:

300

⸻

After eKYC Approved:

Level 3

EKYC VERIFIED

Trust Score:

500

Badge:

EKYC VERIFIED

⸻

BUSINESS RULES

eKYC has higher trust value than KYC.

Verification hierarchy:

EKYC

KYC

REGISTERED

⸻

User may:

Have KYC only

Have eKYC only

Have both

⸻

When eKYC approved:

Highest verification status becomes:

EKYC VERIFIED

⸻

DATABASE TABLES USED

Use:

users

user_profiles

ekyc_submissions

verification_reviews

user_documents

audit_logs

trust_scores

⸻

SUPPORTED EKYC SOURCES

Phase 1:

PDF Upload Only

⸻

Examples:

VNPT eKYC

FPT eKYC

VNeID Export

Bank eKYC Reports

Approved Future Providers

⸻

Design provider-agnostic architecture.

⸻

EKYC STATUS

Supported:

DRAFT

SUBMITTED

PROCESSING

UNDER_REVIEW

APPROVED

REJECTED

EXPIRED

⸻

EKYC FLOW

User

↓

Upload PDF

↓

PDF Parsing

↓

Data Extraction

↓

Validation

↓

Admin Review

↓

Approve / Reject

↓

Trust Upgrade

⸻

PDF PROCESSING

Extract:

Full Name

Date Of Birth

Gender

Nationality

CCCD Number

Issue Date

Issue Place

Address

Verification Result

Verification Timestamp

Provider Name

Verification Reference ID

⸻

Store:

Structured JSON

Raw Extracted Text

Metadata

⸻

PDF VALIDATION

Check:

File Type

PDF Integrity

Maximum Size

Provider Signature (if available)

Required Fields

⸻

Maximum Size:

20 MB

⸻

DOCUMENT STORAGE

Store:

Original PDF

Parsed JSON

Metadata

SHA256 Hash

Provider Name

Verification Reference

⸻

DUPLICATE DETECTION

Check:

CCCD Number

Verification Reference ID

Document Hash

⸻

Flag:

POSSIBLE_DUPLICATE

For Admin Review.

⸻

API 1

Submit eKYC

POST /api/v1/ekyc/upload

⸻

Request:

multipart/form-data

pdf_file

⸻

Response:

{
“success”: true,
“submission_id”: “…”,
“status”: “PROCESSING”
}

⸻

API 2

Get eKYC Status

GET /api/v1/ekyc/status

⸻

Response:

{
“status”: “UNDER_REVIEW”,
“provider”: “VNPT”,
“trust_level_after_approval”: “LEVEL_3”
}

⸻

API 3

Get Parsed Data

GET /api/v1/ekyc/preview

⸻

Owner only.

⸻

Response:

{
“full_name”: “…”,
“cccd_number”: “…”,
“provider”: “VNPT”
}

⸻

PDF PARSER ARCHITECTURE

Create abstraction:

IEKYCProvider

⸻

Implement:

GenericPDFProvider

⸻

Future:

VNPTProvider

FPTProvider

VNeIDProvider

BankProvider

⸻

Do not hardcode one provider.

⸻

DATA EXTRACTION CONFIDENCE

Store:

confidence_score

Range:

0-100

⸻

Below:

80

Flag:

LOW_CONFIDENCE

Manual review required.

⸻

ADMIN REVIEW QUEUE

Create:

EKYC_REVIEW

⸻

Admin sees:

PDF

Parsed Data

Confidence Score

Duplicate Flags

Verification Reference

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

EKYC_VERIFIED event

⸻

Generate audit logs.

⸻

REJECTION FLOW

Admin must provide reason.

Examples:

Invalid PDF

Missing Data

Unrecognized Provider

Document Tampering

Duplicate Identity

Low Confidence

⸻

Store rejection reason.

⸻

SECURITY REQUIREMENTS

Only owner may view PDF.

Admins require:

EKYC_REVIEW permission.

⸻

All document access logged.

⸻

Never expose:

Full CCCD publicly.

⸻

Mask:

079*****789

⸻

AUDIT EVENTS

EKYC_SUBMITTED

EKYC_PROCESSING_STARTED

EKYC_PARSED

EKYC_APPROVED

EKYC_REJECTED

EKYC_DUPLICATE_FLAGGED

⸻

FILES TO CREATE

backend/services/ekyc_service.py

backend/services/pdf_parser_service.py

backend/api/v1/ekyc/routes.py

backend/schemas/ekyc.py

backend/repositories/ekyc_repository.py

backend/providers/ekyc/base_provider.py

backend/providers/ekyc/generic_pdf_provider.py

⸻

PDF LIBRARIES

Approved:

pdfplumber

PyPDF2

pymupdf

Equivalent libraries

⸻

Design parser abstraction.

⸻

TESTING REQUIREMENTS

Create:

tests/unit/ekyc/

tests/integration/ekyc/

tests/security/ekyc/

⸻

Unit Tests:

PDF Validation

PDF Parsing

Confidence Calculation

Duplicate Detection

Trust Upgrade Logic

⸻

Integration Tests:

Upload PDF

Parse PDF

Admin Approval

Admin Rejection

Trust Level Update

⸻

Security Tests:

Unauthorized PDF Access

Document Leakage

Permission Escalation

Direct File Access

Provider Spoofing

⸻

ACCEPTANCE CRITERIA

✓ PDF Upload Works

✓ PDF Parsing Works

✓ Data Extraction Works

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

pytest tests/unit/ekyc -v

pytest tests/integration/ekyc -v

pytest tests/security/ekyc -v

pytest -v

All tests must pass.

⸻

DOCUMENTATION UPDATE

Update:

PROJECT_STATUS_DASHBOARD.md

Change:

Sprint 7

IN PROGRESS

↓

COMPLETED

Update progress percentage.

⸻

COMPLETION REPORT

Create:

SPRINT_7_COMPLETION_REPORT.md

Include:

Summary

PDF Architecture

Provider Architecture

Files Created

APIs Added

Tests Added

Trust Model Impact

Known Issues

Sprint 8 Readiness

⸻

GIT COMMIT

Create commit:

[Sprint-7]

EKYC Module Completed

Push to repository.

⸻

DEFINITION OF DONE

✓ PDF Upload Works

✓ PDF Parsing Works

✓ Admin Review Works

✓ Trust Upgrade Works

✓ Audit Logs Created

✓ Tests Pass

✓ Dashboard Updated

✓ Completion Report Created

✓ Git Commit Created

Only then may Sprint 7 be marked COMPLETE.

END OF DOCUMENT