CODEX_IMPLEMENT_SPRINT_2_REGISTRATION

Role:

You are the Primary Implementation Agent for P2PSuperBot.

Implement Sprint 2 exactly according to approved specifications.

Do not implement future sprints.

Do not redesign business rules.

⸻

PRE-READ REQUIREMENTS

Read in order:

1. PROJECT_STATUS_DASHBOARD.md
2. PROJECT_MEMORY.md
3. 10_PHASE1_MASTER_SPECIFICATION.md
4. 11_PHASE1_IMPLEMENTATION_ROADMAP.md
5. 02_USER_REGISTRATION_FLOW.md
6. 08_API_SERVICE_DESIGN_PHASE1.md
7. 14_CODEX_STARTUP_PROMPT.md

Review Sprint 1 implementation before starting.

⸻

SPRINT INFORMATION

Sprint:

Sprint 2
Registration Module

Goal:

Implement complete Email Registration workflow.

⸻

BUSINESS RULES

Registration requires:

Email Only

Do NOT request:

Phone Number
CCCD
Name
Wallet

during registration.

⸻

System generates automatically:

User ID
Temporary Password
Activation Token

⸻

System sends email containing:

User ID
Temporary Password
Login Guide
2FA Guide
eKYC Guide

⸻

User status after registration:

WAITING_FIRST_LOGIN

⸻

MODULES TO IMPLEMENT

Implement:

AuthService
RegistrationService
EmailService
RegistrationWorker

⸻

DATABASE TABLES USED

Use:

users
user_security
registration_sessions
audit_logs

⸻

API ENDPOINT

Create:

POST /api/v1/auth/register

⸻

Request:

{
  "email": "user@gmail.com"
}

⸻

Response:

{
  "success": true,
  "message": "Registration email sent"
}

⸻

VALIDATION RULES

Email required.

Email format valid.

Email unique.

Case-insensitive uniqueness.

⸻

Reject:

{
  "success": false,
  "error_code": "EMAIL_ALREADY_EXISTS"
}

⸻

USER ID GENERATION

Format:

P2P-XXXXXXXX

Example:

P2P-4F82A7D1

Requirements:

Globally unique.

Immutable.

⸻

TEMPORARY PASSWORD GENERATION

Requirements:

16 Characters
Uppercase
Lowercase
Number
Special Character

Generated automatically.

Stored only as hash.

Never logged.

Never returned via API.

Only sent by email.

⸻

ACTIVATION TOKEN

Generate:

Activation Token

Store:

Hash Only

Expiration:

24 Hours

Store in:

registration_sessions

⸻

EMAIL SERVICE

Create:

backend/integrations/smtp/

Implement:

SMTP Client
Email Templates

⸻

Templates:

Registration Email

⸻

Registration Email must contain:

Welcome Message
User ID
Temporary Password
Login Instructions
2FA Instructions
eKYC Instructions

⸻

EMAIL QUEUE

Do NOT send email directly.

Use worker queue.

⸻

Create:

email_queue

Flow:

API
↓
Service
↓
Queue
↓
Worker
↓
SMTP

⸻

AUDIT LOGGING

Create audit record:

USER_REGISTERED

Metadata:

{
  "email": "...",
  "user_id": "..."
}

⸻

RATE LIMITING

Registration:

5 requests / hour / IP

Implement Redis-based rate limiting.

⸻

SECURITY REQUIREMENTS

Never expose:

Password Hash
Activation Token Hash

⸻

Mask email in logs.

Example:

hu***@gmail.com

⸻

FILES TO CREATE

Create:

backend/api/v1/auth/routes.py
backend/services/auth_service.py
backend/services/registration_service.py
backend/services/email_service.py
backend/workers/email_worker.py
backend/integrations/smtp/client.py
backend/schemas/auth.py

⸻

TESTING REQUIREMENTS

Create:

tests/unit/auth/
tests/integration/auth/

⸻

Unit Tests:

Email Validation
User ID Generation
Temporary Password Generation
Activation Token Generation
Rate Limiting

⸻

Integration Tests:

Registration API
Duplicate Email
Registration Session Creation
Audit Log Creation
Email Queue Creation

⸻

ACCEPTANCE CRITERIA

✓ User created

✓ User ID generated

✓ Temporary password generated

✓ Password hashed

✓ Registration session created

✓ Activation token created

✓ Email queued

✓ Audit log created

✓ API returns success

✓ Duplicate email blocked

✓ Unit tests pass

✓ Integration tests pass

⸻

VALIDATION COMMANDS

Run:

pytest tests/unit/auth -v

Run:

pytest tests/integration/auth -v

Run:

pytest -v

All tests must pass.

⸻

DOCUMENTATION UPDATE

Update:

PROJECT_STATUS_DASHBOARD.md

Change:

Sprint 2
IN PROGRESS
↓
COMPLETED

Update progress percentage.

⸻

COMPLETION REPORT

Create:

SPRINT_2_COMPLETION_REPORT.md

Include:

1. Summary
2. Files Created
3. Files Modified
4. APIs Added
5. Tests Added
6. Test Results
7. Known Issues
8. Sprint 3 Readiness

⸻

GIT COMMIT

Create commit:

[Sprint-2]
Registration Module Completed

Push to repository.

⸻

DEFINITION OF DONE

Sprint 2 is complete only when:

✓ Registration API Works

✓ User Created

✓ User ID Generated

✓ Temporary Password Generated

✓ Email Queued

✓ Audit Log Created

✓ Tests Pass

✓ Dashboard Updated

✓ Completion Report Created

✓ Git Commit Created

Only then may Sprint 2 be marked COMPLETE.

END OF DOCUMENT