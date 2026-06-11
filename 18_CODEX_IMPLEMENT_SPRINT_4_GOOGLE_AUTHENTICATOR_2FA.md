CODEX_IMPLEMENT_SPRINT_4_GOOGLE_AUTHENTICATOR_2FA

Role:

You are the Primary Implementation Agent for P2PSuperBot.

Implement Sprint 4 exactly according to approved specifications.

Do not redesign business logic.

Do not implement future sprints.

⸻

PRE-READ REQUIREMENTS

Read in order:

1. PROJECT_STATUS_DASHBOARD.md
2. PROJECT_MEMORY.md
3. 10_PHASE1_MASTER_SPECIFICATION.md
4. 11_PHASE1_IMPLEMENTATION_ROADMAP.md
5. 03_LOGIN_SECURITY_2FA_FLOW.md
6. 08_API_SERVICE_DESIGN_PHASE1.md
7. 14_CODEX_STARTUP_PROMPT.md

Review Sprint 1, Sprint 2 and Sprint 3 implementation before starting.

⸻

SPRINT INFORMATION

Sprint:

Sprint 4
Google Authenticator & 2FA

Goal:

Implement mandatory Two-Factor Authentication.

⸻

BUSINESS RULES

Approved Decision:

User cannot become ACTIVE
until:
Password Changed
AND
2FA Enabled

⸻

After first login:

State:

2FA_PENDING

⸻

After successful 2FA setup:

State:

ACTIVE

⸻

APPROVED AUTHENTICATORS

Supported:

Google Authenticator
Microsoft Authenticator
Authy

⸻

Protocol:

RFC6238 TOTP

⸻

FEATURES TO IMPLEMENT

Implement:

TOTP Secret Generation
QR Code Generation
2FA Setup
2FA Verification
Recovery Codes
Recovery Code Login
Disable 2FA
Re-enable 2FA

⸻

DATABASE TABLES USED

Use:

user_security
recovery_codes
audit_logs

⸻

SECURITY MODEL

Store:

TOTP Secret

Encrypted at rest.

Never return raw secret after setup.

⸻

Store:

Recovery Codes

Hashed only.

Never store plaintext recovery codes.

⸻

API 1

2FA Setup

Create:

POST /api/v1/auth/2fa/setup

⸻

Requirements:

Authenticated user.

Password already changed.

⸻

Response:

{
  "qr_code": "base64...",
  "manual_key": "XXXXX..."
}

⸻

Generate:

TOTP Secret
otpauth URI
QR Code

Compatible with:

Google Authenticator
Microsoft Authenticator
Authy

⸻

API 2

Verify Initial 2FA

Create:

POST /api/v1/auth/2fa/verify

⸻

Request:

{
  "code": "123456"
}

⸻

Validation:

RFC6238

6 digits

30 second window

⸻

Success:

{
  "success": true,
  "status": "ACTIVE"
}

⸻

System:

Activate 2FA.

Generate recovery codes.

Create audit log.

⸻

RECOVERY CODES

Generate:

10 Recovery Codes

Format:

ABCD-EFGH-IJKL

⸻

Requirements:

Single-use only.

Stored hashed.

⸻

User receives:

{
  "recovery_codes": [
    "...."
  ]
}

One time only.

Never shown again.

⸻

LOGIN FLOW UPDATE

Update Sprint 3 login.

If:

2FA Enabled

System must return:

{
  "requires_2fa": true
}

⸻

User submits:

POST /api/v1/auth/2fa/login

Request:

{
  "code": "123456"
}

⸻

Success:

Issue:

Access Token
Refresh Token

Create session.

⸻

RECOVERY LOGIN

Create:

POST /api/v1/auth/2fa/recovery

⸻

Request:

{
  "recovery_code": "ABCD-EFGH-IJKL"
}

⸻

Success:

Login Successful

⸻

Mark code:

USED

Cannot reuse.

⸻

DISABLE 2FA

Create:

POST /api/v1/auth/2fa/disable

⸻

Requirements:

Password

AND

Valid TOTP

⸻

Request:

{
  "password": "...",
  "code": "123456"
}

⸻

Success:

{
  "success": true
}

⸻

System:

Disable 2FA.

Invalidate recovery codes.

Generate audit log.

⸻

RE-ENABLE 2FA

Must:

Generate:

New Secret
New Recovery Codes

Old recovery codes become invalid.

⸻

SECURITY REQUIREMENTS

Reject:

Expired Codes
Invalid Codes
Reused Recovery Codes

⸻

Allow clock drift:

±1 TOTP Window

Maximum:

30 Seconds Before
30 Seconds After

⸻

AUDIT EVENTS

Generate:

2FA_SETUP_STARTED
2FA_ENABLED
2FA_LOGIN_SUCCESS
2FA_LOGIN_FAILED
2FA_DISABLED
RECOVERY_CODE_USED

⸻

FILES TO CREATE

Create:

backend/security/totp.py
backend/services/two_factor_service.py
backend/api/v1/auth/two_factor_routes.py

⸻

Update:

backend/services/auth_service.py
backend/security/jwt.py

if required.

⸻

LIBRARIES

Use:

pyotp
qrcode

or equivalent approved libraries.

⸻

TESTING REQUIREMENTS

Create:

tests/unit/2fa/
tests/integration/2fa/
tests/security/2fa/

⸻

Unit Tests:

Secret Generation
TOTP Validation
Recovery Code Generation
Recovery Code Validation
Disable Flow

⸻

Integration Tests:

2FA Setup
QR Generation
Verification
2FA Login
Recovery Login

⸻

Security Tests:

Expired Code
Invalid Code
Bruteforce Attempt
Recovery Code Reuse
Clock Drift Validation

⸻

ACCEPTANCE CRITERIA

✓ QR Code Generated

✓ Google Authenticator Compatible

✓ TOTP Validation Works

✓ Recovery Codes Generated

✓ Recovery Codes Single Use

✓ 2FA Login Works

✓ Disable Flow Works

✓ Audit Logs Created

✓ Unit Tests Pass

✓ Integration Tests Pass

✓ Security Tests Pass

⸻

VALIDATION COMMANDS

Run:

pytest tests/unit/2fa -v

Run:

pytest tests/integration/2fa -v

Run:

pytest tests/security/2fa -v

Run:

pytest -v

All tests must pass.

⸻

DOCUMENTATION UPDATE

Update:

PROJECT_STATUS_DASHBOARD.md

Change:

Sprint 4
IN PROGRESS
↓
COMPLETED

Update progress percentage.

⸻

COMPLETION REPORT

Create:

SPRINT_4_COMPLETION_REPORT.md

Include:

1. Summary
2. Security Features Added
3. APIs Added
4. Recovery Code Design
5. Tests Added
6. Test Results
7. Known Issues
8. Sprint 5 Readiness

⸻

GIT COMMIT

Create commit:

[Sprint-4]
Google Authenticator 2FA Completed

Push to repository.

⸻

DEFINITION OF DONE

Sprint 4 is complete only when:

✓ QR Setup Works

✓ Google Authenticator Works

✓ TOTP Login Works

✓ Recovery Codes Work

✓ Disable Flow Works

✓ Audit Logs Created

✓ Tests Pass

✓ Dashboard Updated

✓ Completion Report Created

✓ Git Commit Created

Only then may Sprint 4 be marked COMPLETE.

END OF DOCUMENT