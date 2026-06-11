P2PSuperBot — Phase 1 Implementation Roadmap

Version: 1.0

Status: Approved

Purpose:

This roadmap defines the execution order for Phase 1 implementation.

Each sprint must:

* Be independently testable
* Be independently reviewable
* Pass all tests before continuing
* Be committed to Git before starting the next sprint

Rule:

No sprint may start until the previous sprint is fully completed.

⸻

Sprint 0 — Environment & Foundation

Objective:

Prepare development environment.

Tasks:

* Python Environment
* PostgreSQL
* Redis
* Docker (optional)
* Git Repository
* CI/CD Foundation
* Dependency Management

Deliverables:

* requirements.txt
* requirements-dev.txt
* pytest configuration
* lint configuration

Acceptance Criteria:

✓ Environment operational

✓ Database connection working

✓ Redis connection working

✓ Test framework operational

✓ Git repository initialized

Status:

Completed

⸻

Sprint 1 — Core Database Foundation

Objective:

Create database schema.

Tables:

users

user_security

registration_sessions

user_sessions

recovery_codes

audit_logs

Tasks:

* SQLAlchemy Models
* Alembic Migrations
* Repository Layer
* Base CRUD

Deliverables:

backend/models/

backend/repositories/

alembic/

Acceptance Criteria:

✓ Migration runs successfully

✓ Database schema created

✓ CRUD tests pass

⸻

Sprint 2 — Registration Module

Objective:

Implement user registration.

Features:

* Email Registration
* User ID Generation
* Temporary Password Generation
* Activation Token Generation
* Registration Email

APIs:

POST /api/v1/auth/register

Deliverables:

AuthService

Registration Worker

SMTP Integration

Acceptance Criteria:

✓ User created

✓ Email sent

✓ Temporary password generated

✓ Audit log created

⸻

Sprint 3 — Authentication Module

Objective:

Implement login and password lifecycle.

Features:

* Login
* Password Validation
* Password Change
* Password Reset
* Session Creation

APIs:

POST /api/v1/auth/login

POST /api/v1/auth/change-password

POST /api/v1/auth/reset-password

Acceptance Criteria:

✓ Login works

✓ Password change works

✓ Password reset works

✓ Session management works

✓ Lockout policy works

⸻

Sprint 4 — Google Authenticator (2FA)

Objective:

Implement TOTP security.

Features:

* QR Generation
* TOTP Validation
* Recovery Codes
* 2FA Enforcement

APIs:

POST /api/v1/auth/2fa/setup

POST /api/v1/auth/2fa/verify

Acceptance Criteria:

✓ QR generated

✓ TOTP verified

✓ Recovery codes generated

✓ Login requires 2FA

⸻

Sprint 5 — User Profile Module

Objective:

Implement user profile management.

Tables:

user_profiles

user_identity_documents

Features:

* Profile View
* Profile Update
* Data Masking

APIs:

GET /api/v1/profile

PUT /api/v1/profile

Acceptance Criteria:

✓ Profile displayed

✓ Profile updated

✓ Sensitive data masked

⸻

Sprint 6 — KYC Module

Objective:

Implement manual KYC.

Tables:

kyc_submissions

user_documents

Features:

* CCCD Front Upload
* CCCD Back Upload
* Selfie Upload
* OCR Processing

APIs:

POST /api/v1/kyc/submit

GET /api/v1/kyc/status

Acceptance Criteria:

✓ Upload works

✓ OCR works

✓ Review record created

✓ Status tracking works

⸻

Sprint 7 — eKYC Module

Objective:

Implement PDF-based eKYC.

Tables:

ekyc_submissions

verification_reviews

Features:

* PDF Upload
* PDF Parsing
* Structured Data Extraction

APIs:

POST /api/v1/ekyc/upload

GET /api/v1/ekyc/status

Acceptance Criteria:

✓ PDF upload works

✓ Parsing works

✓ Review queue works

⸻

Sprint 8 — Wallet Module

Objective:

Implement wallet registration and verification.

Tables:

user_wallets

wallet_verifications

Features:

* Add Wallet
* Wallet Categories
* Verification Workflow

Networks:

* TRON
* BSC

APIs:

POST /api/v1/wallets

GET /api/v1/wallets

Acceptance Criteria:

✓ Wallet added

✓ Wallet verified

✓ Duplicate detection works

⸻

Sprint 9 — Credit System

Objective:

Implement internal credits.

Tables:

credit_accounts

credit_ledger

Features:

* Credit Issuance
* Credit Consumption
* Ledger Tracking

APIs:

GET /api/v1/credits/balance

GET /api/v1/credits/ledger

Acceptance Criteria:

✓ Credits issued

✓ Credits consumed

✓ Ledger accurate

⸻

Sprint 10 — Admin Review System

Objective:

Implement admin operations.

Tables:

admin_users

admin_roles

review_queue

verification_reviews

Features:

* KYC Review
* eKYC Review
* Wallet Review
* Credit Adjustment

APIs:

/admin/*

Acceptance Criteria:

✓ Approve works

✓ Reject works

✓ Review queue works

✓ Audit logs generated

⸻

Sprint 11 — Security & Compliance

Objective:

Strengthen platform security.

Features:

* Rate Limiting
* Suspicious Activity Detection
* Security Alerts
* Permission Enforcement

Tables:

security_alerts

Acceptance Criteria:

✓ Rate limiting active

✓ Alerts generated

✓ Permissions enforced

⸻

Sprint 12 — Telegram Bot Integration

Objective:

Connect Telegram Bot to backend.

Commands:

/register

/login

/profile

/kyc

/ekyc

/add_wallet

/credits

Features:

* Command Routing
* Session Validation
* Notification Delivery

Acceptance Criteria:

✓ Commands work

✓ API integration works

✓ Notifications delivered

⸻

Sprint 13 — Audit & Monitoring

Objective:

Implement operational visibility.

Features:

* Audit Dashboard
* Health Checks
* Readiness Checks
* Metrics

Endpoints:

GET /health

GET /ready

Acceptance Criteria:

✓ Monitoring active

✓ Audit searchable

✓ Health endpoints operational

⸻

Sprint 14 — Integration Testing

Objective:

Validate end-to-end workflows.

Flows:

Registration
↓
Login
↓
2FA
↓
Profile
↓
KYC/eKYC
↓
Wallet
↓
Credits

Acceptance Criteria:

✓ Full workflow passes

✓ No blocking defects

✓ Database integrity validated

⸻

Sprint 15 — Security Testing

Objective:

Validate platform security.

Tests:

* Authentication
* Authorization
* Rate Limiting
* Session Security
* Data Masking

Acceptance Criteria:

✓ Security tests pass

✓ No critical vulnerabilities

⸻

Sprint 16 — Release Candidate

Objective:

Prepare production release.

Tasks:

* Documentation Review
* Environment Review
* Migration Validation
* Backup Procedures
* Deployment Scripts

Acceptance Criteria:

✓ Production Ready

✓ Release Approved

✓ Git Tag Created

⸻

Definition of Done (DoD)

Each sprint is complete only when:

✓ Code Implemented

✓ Unit Tests Pass

✓ Integration Tests Pass

✓ Documentation Updated

✓ Git Commit Created

✓ Git Push Completed

✓ Sprint Review Approved

⸻

Mandatory Reading Order For Codex

Before coding:

1. 10_PHASE1_MASTER_SPECIFICATION.md

Then:

2. Relevant Detailed Specification

Examples:

Authentication:

* 03_LOGIN_SECURITY_2FA_FLOW.md

KYC:

* 04_PROFILE_KYC_EKYC_FLOW.md

Wallet:

* 05_WALLET_CREDIT_FLOW.md

Database:

* 07_DATABASE_DESIGN_PHASE1.md

API:

* 08_API_SERVICE_DESIGN_PHASE1.md

Bot:

* 09_BOT_COMMANDS_PHASE1.md

No coding may begin without reading the Master Specification first.

End of Roadmap