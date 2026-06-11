P2PSuperBot — API & Service Design Phase 1

1. Objective

This document defines:

* API Architecture
* Service Architecture
* Repository Architecture
* Worker Architecture
* Redis Usage
* Queue Processing
* Telegram Bot Integration

Phase 1 supports:

Register
Login
2FA
Profile
KYC
eKYC
Wallet
Credits
Admin Review

⸻

2. High Level Architecture

Telegram User
        │
        ▼
Telegram Bot
        │
        ▼
FastAPI Backend
        │
 ┌──────┼──────┐
 ▼      ▼      ▼
Redis  Worker PostgreSQL

⸻

3. Responsibilities

Telegram Bot

Responsible for:

Receive Commands
Validate Input Format
Display Results
Send Notifications

Bot must NOT:

Parse PDF
Run OCR
Check Blockchain
Generate Reports
Perform Heavy Queries

⸻

FastAPI Backend

Responsible for:

Business Logic
Authentication
Authorization
Validation
API Endpoints
Database Operations

⸻

Redis

Responsible for:

Cache
Session Cache
Rate Limit
Task Queue
Temporary Tokens

⸻

Worker

Responsible for:

Send Email
OCR Processing
PDF Parsing
Wallet Verification
Credit Processing
Background Tasks

⸻

PostgreSQL

Responsible for:

Persistent Storage

⸻

4. Project Structure

backend/
├── api/
├── services/
├── repositories/
├── models/
├── schemas/
├── workers/
├── security/
├── core/
├── integrations/
└── utils/

⸻

5. API Layer

Path:

backend/api/v1/

⸻

Modules:

auth
users
profile
kyc
ekyc
wallet
credits
admin
health

⸻

Example:

backend/api/v1/auth/routes.py

⸻

6. Service Layer

Path:

backend/services/

Contains business logic only.

⸻

Example:

AuthService
UserService
ProfileService
KYCService
EKYCService
WalletService
CreditService
AdminReviewService

⸻

Rules:

Services must not know:

Telegram
FastAPI Request Objects

⸻

7. Repository Layer

Path:

backend/repositories/

Responsible for:

Database Access Only

⸻

Examples:

UserRepository
WalletRepository
CreditRepository
ReviewRepository

⸻

No business logic allowed.

⸻

8. Security Layer

Path:

backend/security/

Modules:

password.py
jwt.py
totp.py
permissions.py

⸻

Responsibilities:

Hash Password
Verify Password
Generate JWT
Validate JWT
Generate TOTP
Validate TOTP

⸻

9. Integration Layer

Path:

backend/integrations/

External systems.

⸻

Examples:

telegram/
smtp/
tron/
bsc/
ocr/
pdf_parser/

⸻

Rules:

No business logic.

Only adapters.

⸻

10. Register API

Endpoint:

POST /api/v1/auth/register

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

Flow:

API
↓
AuthService
↓
UserRepository
↓
Queue Email Task

⸻

11. Login API

Endpoint:

POST /api/v1/auth/login

Request:

{
  "email": "...",
  "password": "..."
}

⸻

Response:

{
  "requires_password_change": true
}

or

{
  "requires_2fa": true
}

⸻

12. Password Change API

Endpoint:

POST /api/v1/auth/change-password

⸻

Requirements:

Valid Session

⸻

13. 2FA APIs

Setup:

POST /api/v1/auth/2fa/setup

⸻

Verify:

POST /api/v1/auth/2fa/verify

⸻

Disable:

POST /api/v1/auth/2fa/disable

Requires:

Password
2FA

⸻

14. Profile APIs

Get Profile:

GET /api/v1/profile

⸻

Update Profile:

PUT /api/v1/profile

⸻

15. KYC APIs

Submit:

POST /api/v1/kyc/submit

Uploads:

CCCD Front
CCCD Back
Selfie

⸻

Status:

GET /api/v1/kyc/status

⸻

16. eKYC APIs

Submit:

POST /api/v1/ekyc/upload

Upload:

PDF

⸻

Status:

GET /api/v1/ekyc/status

⸻

17. Wallet APIs

Add Wallet:

POST /api/v1/wallets

⸻

List Wallets:

GET /api/v1/wallets

⸻

Verification Request:

POST /api/v1/wallets/{id}/verify

⸻

Status:

GET /api/v1/wallets/{id}

⸻

18. Credits APIs

Balance:

GET /api/v1/credits/balance

⸻

Ledger:

GET /api/v1/credits/ledger

⸻

19. Admin APIs

Pending Reviews:

GET /api/v1/admin/reviews

⸻

Approve:

POST /api/v1/admin/reviews/{id}/approve

⸻

Reject:

POST /api/v1/admin/reviews/{id}/reject

⸻

20. Health APIs

Health Check:

GET /health

⸻

Readiness:

GET /ready

⸻

21. Worker Jobs

Queue Name:

email_queue

Jobs:

Send Registration Email
Password Reset Email

⸻

Queue:

ocr_queue

Jobs:

OCR CCCD
OCR Selfie

⸻

Queue:

pdf_queue

Jobs:

Parse eKYC PDF

⸻

Queue:

wallet_queue

Jobs:

Verify Wallet
Check Blockchain

⸻

Queue:

credit_queue

Jobs:

Issue Credits
Consume Credits

⸻

22. Redis Usage

Keys:

login_attempts
session_cache
2fa_setup
password_reset
rate_limit

⸻

TTL Examples:

Login Lock:
15 minutes
Password Reset:
30 minutes
2FA Setup:
30 minutes

⸻

23. Rate Limiting

Register:

5/hour

⸻

Login:

10/minute

⸻

Password Reset:

3/hour

⸻

24. Error Handling

Standard Response:

{
  "success": false,
  "error_code": "INVALID_EMAIL",
  "message": "Invalid email format"
}

⸻

25. Acceptance Criteria

Architecture is complete when:

✓ Bot only handles interaction

✓ Backend handles business logic

✓ Services contain business logic

✓ Repositories contain DB access only

✓ Workers handle heavy jobs

✓ Redis handles cache and queues

✓ PostgreSQL handles persistence

✓ APIs defined

✓ Security layer isolated

✓ External integrations isolated

✓ Ready for Codex implementation