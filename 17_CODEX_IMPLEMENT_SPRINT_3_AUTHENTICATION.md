CODEX_IMPLEMENT_SPRINT_3_AUTHENTICATION

Role:

You are the Primary Implementation Agent for P2PSuperBot.

Implement Sprint 3 exactly according to approved specifications.

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

Review Sprint 1 and Sprint 2 implementation before starting.

⸻

SPRINT INFORMATION

Sprint:

Sprint 3
Authentication Module

Goal:

Implement secure authentication lifecycle.

⸻

BUSINESS RULES

Supported Login:

Email
OR
User ID

⸻

Authentication requires:

Password

⸻

First Login:

Force Password Change

User cannot continue until:

Password Changed

⸻

After password change:

Require 2FA Setup

(2FA functionality implemented in Sprint 4)

For Sprint 3:

System must support:

2FA_PENDING state

⸻

FEATURES TO IMPLEMENT

Implement:

Login
Password Change
Password Reset
Session Creation
Session Validation
Session Revocation
Account Lockout

⸻

DATABASE TABLES USED

Use:

users
user_security
user_sessions
registration_sessions
audit_logs

⸻

AUTHENTICATION STATES

Supported states:

WAITING_FIRST_LOGIN
PASSWORD_CHANGE_REQUIRED
2FA_PENDING
ACTIVE
LOCKED
SUSPENDED

⸻

LOGIN API

Create:

POST /api/v1/auth/login

⸻

Request:

{
  "identifier": "user@gmail.com",
  "password": "MyPassword123!"
}

identifier supports:

Email
User ID

⸻

Success Response:

{
  "success": true,
  "requires_password_change": false,
  "requires_2fa": false,
  "access_token": "...",
  "refresh_token": "..."
}

⸻

First Login Response:

{
  "success": true,
  "requires_password_change": true
}

⸻

PASSWORD CHANGE API

Create:

POST /api/v1/auth/change-password

⸻

Request:

{
  "current_password": "...",
  "new_password": "..."
}

⸻

Rules:

Current password required.

New password must meet policy.

Cannot reuse current password.

⸻

Success:

{
  "success": true,
  "requires_2fa_setup": true
}

⸻

PASSWORD POLICY

Minimum:

12 Characters
1 Uppercase
1 Lowercase
1 Number
1 Special Character

⸻

Passwords:

Never Logged
Never Stored Plaintext
Stored As Argon2/Bcrypt Hash

⸻

PASSWORD RESET REQUEST

Create:

POST /api/v1/auth/reset-password

⸻

Request:

{
  "email": "user@gmail.com"
}

⸻

System:

Generate reset token.

Queue reset email.

Store token hash only.

⸻

Expiration:

30 Minutes

⸻

PASSWORD RESET CONFIRM

Create:

POST /api/v1/auth/reset-password/confirm

⸻

Request:

{
  "token": "...",
  "new_password": "..."
}

⸻

Success:

{
  "success": true
}

⸻

JWT IMPLEMENTATION

Implement:

Access Token
Refresh Token

⸻

Access Token:

15 Minutes

⸻

Refresh Token:

30 Days

⸻

Algorithm:

HS256

⸻

Claims:

{
  "sub": "user_id",
  "user_code": "P2P-XXXX",
  "role": "USER"
}

⸻

REFRESH TOKEN API

Create:

POST /api/v1/auth/refresh

⸻

Request:

{
  "refresh_token": "..."
}

⸻

Response:

{
  "access_token": "...",
  "refresh_token": "..."
}

⸻

LOGOUT API

Create:

POST /api/v1/auth/logout

⸻

Requirements:

Valid session.

⸻

System:

Invalidate refresh token.

Deactivate session.

Create audit log.

⸻

SESSION MANAGEMENT

Create session record:

user_sessions

Store:

User ID
Device Info
IP Address
Refresh Token Hash
Expiry

⸻

Support:

Multiple Devices

⸻

ACCOUNT LOCKOUT

Rule:

5 Failed Login Attempts

⸻

Action:

LOCK ACCOUNT

Duration:

15 Minutes

⸻

Store:

failed_login_count
locked_until

⸻

RATE LIMITING

Login:

10 requests / minute / IP

⸻

Password Reset:

3 requests / hour / IP

⸻

Use Redis.

⸻

AUDIT EVENTS

Generate:

LOGIN_SUCCESS
LOGIN_FAILED
PASSWORD_CHANGED
PASSWORD_RESET_REQUESTED
PASSWORD_RESET_COMPLETED
LOGOUT

⸻

FILES TO CREATE

Create:

backend/security/password.py
backend/security/jwt.py
backend/services/auth_service.py
backend/services/session_service.py
backend/api/v1/auth/routes.py
backend/schemas/auth.py

⸻

FILES TO UPDATE

Update:

users
user_security
user_sessions

repositories if required.

⸻

TESTING REQUIREMENTS

Create:

tests/unit/auth/
tests/integration/auth/
tests/security/auth/

⸻

Unit Tests:

Password Validation
Password Hashing
JWT Creation
JWT Validation
Session Creation
Session Revocation

⸻

Integration Tests:

Login
Password Change
Password Reset
Refresh Token
Logout

⸻

Security Tests:

Invalid JWT
Expired JWT
Brute Force Lockout
Token Tampering
Password Policy Enforcement

⸻

ACCEPTANCE CRITERIA

✓ Login works

✓ Password change works

✓ Password reset works

✓ JWT works

✓ Refresh token works

✓ Session tracking works

✓ Logout works

✓ Lockout works

✓ Audit logs created

✓ Unit tests pass

✓ Integration tests pass

✓ Security tests pass

⸻

VALIDATION COMMANDS

Run:

pytest tests/unit/auth -v

Run:

pytest tests/integration/auth -v

Run:

pytest tests/security/auth -v

Run:

pytest -v

All tests must pass.

⸻

DOCUMENTATION UPDATE

Update:

PROJECT_STATUS_DASHBOARD.md

Change:

Sprint 3
IN PROGRESS
↓
COMPLETED

Update progress percentage.

⸻

COMPLETION REPORT

Create:

SPRINT_3_COMPLETION_REPORT.md

Include:

1. Summary
2. APIs Added
3. Security Features Added
4. Files Created
5. Files Modified
6. Tests Added
7. Test Results
8. Sprint 4 Readiness

⸻

GIT COMMIT

Create commit:

[Sprint-3]
Authentication Module Completed

Push to repository.

⸻

DEFINITION OF DONE

Sprint 3 is complete only when:

✓ Login API Works

✓ Password Change Works

✓ Password Reset Works

✓ JWT Works

✓ Refresh Token Works

✓ Session Tracking Works

✓ Account Lockout Works

✓ Audit Logs Created

✓ Tests Pass

✓ Dashboard Updated

✓ Completion Report Created

✓ Git Commit Created

Only then may Sprint 3 be marked COMPLETE.

END OF DOCUMENT