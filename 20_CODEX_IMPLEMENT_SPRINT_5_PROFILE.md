CODEX_IMPLEMENT_SPRINT_5_PROFILE

Role:

You are the Primary Implementation Agent for P2PSuperBot.

Implement Sprint 5 exactly according to approved specifications.

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
7. 08_API_SERVICE_DESIGN_PHASE1.md
8. 14_CODEX_STARTUP_PROMPT.md

Review Sprint 1–4 implementation before starting.

⸻

SPRINT INFORMATION

Sprint:

Sprint 5

Profile Module

Goal:

Implement complete user profile management and trust profile foundation.

⸻

BUSINESS OBJECTIVE

Profile is the central identity object.

Every future module:

* KYC
* eKYC
* Wallet
* Reputation
* Trust Score
* TXID Network

will connect to Profile.

Profile must be designed for long-term expansion.

⸻

DATABASE TABLES USED

Use:

user_profiles

users

user_security

audit_logs

⸻

PROFILE STATUS

Supported:

PROFILE_INCOMPLETE

PROFILE_COMPLETED

PROFILE_LOCKED

⸻

PROFILE FIELDS

Basic Information:

First Name

Middle Name

Last Name

Display Name

Date Of Birth

Gender

Nationality

Country

Province

District

Address

Phone Number

Telegram Username

Avatar URL

Bio

⸻

DATA CLASSIFICATION

Public:

Display Name

Avatar

Trust Level

Trust Score

Join Date

Badges

⸻

Private:

Phone Number

Address

Date Of Birth

Nationality

⸻

Sensitive:

CCCD

Passport

eKYC Data

Never exposed publicly.

⸻

DATA MASKING RULES

Phone:

097****677

Email:

hu***@gmail.com

Wallet:

TAbc****XYZ

CCCD:

079*****789

⸻

PROFILE APIs

Create:

GET /api/v1/profile/me

PUT /api/v1/profile/me

GET /api/v1/profile/public/{user_code}

⸻

GET PROFILE

Returns:

Personal profile

Trust level

Verification status

Badges

Wallet count

Credits balance summary

⸻

UPDATE PROFILE

Allow updating:

Display Name

Phone

Address

Avatar

Bio

Telegram Username

⸻

Cannot update:

User ID

Email

Trust Level

Verification Level

⸻

PUBLIC PROFILE

Return:

User Code

Display Name

Trust Level

Trust Score

Badges

Wallet Count

Transaction Count

Join Date

⸻

Never expose:

Phone

Email

Address

DOB

CCCD

Recovery Codes

2FA Data

⸻

AVATAR SUPPORT

Support:

Avatar URL

Future:

File Upload

CDN Storage

⸻

PROFILE COMPLETENESS SCORE

Calculate:

0 - 100%

Fields weighted:

Display Name

Phone

DOB

Address

Avatar

Telegram Username

Bio

⸻

Used later for:

Trust Model

Community Ranking

⸻

TRUST INTEGRATION

Connect with:

trust_level

trust_score

verification_status

badges

⸻

Read-only in Sprint 5.

No manual modification allowed.

⸻

AUDIT EVENTS

PROFILE_CREATED

PROFILE_UPDATED

AVATAR_UPDATED

PHONE_UPDATED

ADDRESS_UPDATED

⸻

SECURITY REQUIREMENTS

All profile updates:

Require authentication.

Sensitive fields:

Logged to audit trail.

No profile updates via group chat.

Private channel only.

⸻

FILES TO CREATE

backend/services/profile_service.py

backend/api/v1/profile/routes.py

backend/schemas/profile.py

backend/repositories/profile_repository.py

⸻

TESTING REQUIREMENTS

Create:

tests/unit/profile/

tests/integration/profile/

tests/security/profile/

⸻

Unit Tests:

Profile Validation

Masking Logic

Completeness Score

Trust Mapping

⸻

Integration Tests:

Create Profile

Update Profile

Read Profile

Read Public Profile

⸻

Security Tests:

Unauthorized Access

Data Leakage

Sensitive Field Exposure

Profile Enumeration

⸻

ACCEPTANCE CRITERIA

✓ Profile Created

✓ Profile Updated

✓ Public Profile Works

✓ Sensitive Data Hidden

✓ Completeness Score Works

✓ Audit Logs Created

✓ Unit Tests Pass

✓ Integration Tests Pass

✓ Security Tests Pass

⸻

VALIDATION COMMANDS

pytest tests/unit/profile -v

pytest tests/integration/profile -v

pytest tests/security/profile -v

pytest -v

All tests must pass.

⸻

DOCUMENTATION UPDATE

Update:

PROJECT_STATUS_DASHBOARD.md

Change:

Sprint 5

IN PROGRESS

↓

COMPLETED

⸻

COMPLETION REPORT

Create:

SPRINT_5_COMPLETION_REPORT.md

Include:

Summary

Files Created

APIs Added

Tests Added

Profile Design Decisions

Known Issues

Sprint 6 Readiness

⸻

GIT COMMIT

Create commit:

[Sprint-5]

Profile Module Completed

Push to repository.

⸻

DEFINITION OF DONE

✓ Profile APIs Work

✓ Public Profile Works

✓ Data Masking Works

✓ Audit Logs Created

✓ Tests Pass

✓ Dashboard Updated

✓ Completion Report Created

✓ Git Commit Created

Only then may Sprint 5 be marked COMPLETE.

END OF DOCUMENT