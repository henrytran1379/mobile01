CODEX_IMPLEMENT_SPRINT_9_CREDIT_SYSTEM

Role:

You are the Primary Implementation Agent for P2PSuperBot.

Implement Sprint 9 exactly according to approved specifications.

Do not redesign business logic.

Do not implement future sprints.

⸻

PRE-READ REQUIREMENTS

Read in order:

1. PROJECT_STATUS_DASHBOARD.md
2. PROJECT_MEMORY.md
3. TRUST_VERIFICATION_MODEL.md
4. 05_WALLET_CREDIT_FLOW.md
5. 10_PHASE1_MASTER_SPECIFICATION.md
6. 11_PHASE1_IMPLEMENTATION_ROADMAP.md
7. 14_CODEX_STARTUP_PROMPT.md

Review Sprint 1–8 implementation before starting.

⸻

SPRINT INFORMATION

Sprint:

Sprint 9

Credit System

Goal:

Implement complete internal credit economy.

⸻

BUSINESS OBJECTIVE

Credits are:

Internal Utility Units

Used to consume services.

⸻

Credits are NOT:

Currency

Cryptocurrency

Stablecoin

Asset

Investment

Security

⸻

Credits cannot:

Transfer

Withdraw

Trade

Sell

Exchange

⸻

DATABASE TABLES USED

Use:

credit_accounts

credit_ledger

users

audit_logs

subscriptions

trust_scores

⸻

CREDIT ACCOUNT

Each user has:

One Credit Account

⸻

Fields:

Current Balance

Lifetime Earned

Lifetime Consumed

Lifetime Expired

Last Activity

⸻

CREDIT SOURCES

Source 1

Wallet Verification

TRON:

50 TRX

↓

500 Credits

⸻

Source 2

BNB Verification

Configurable

⸻

Source 3

Manual Admin Grant

⸻

Source 4

Promotional Campaigns

Future

⸻

Source 5

Charity Contribution Bonus

Future

⸻

CREDIT TYPES

VERIFICATION_REWARD

ADMIN_GRANT

PROMOTION

SUBSCRIPTION_BONUS

CHARITY_BONUS

⸻

CREDIT CONSUMPTION

Credits used for:

Wallet Lookup

Identity Lookup

TXID Analysis

Risk Analysis

AI Assistant

Advanced Reports

Future Features

⸻

CREDIT LEDGER

All balance changes must create ledger records.

⸻

Ledger Fields:

User

Amount

Type

Direction

Balance Before

Balance After

Reference

Metadata

Timestamp

⸻

DIRECTION

CREDIT

DEBIT

⸻

IMMUTABLE LEDGER

Ledger entries:

Never editable

Never deletable

⸻

Append-only model.

⸻

CREDIT API

API 1

GET /api/v1/credits/balance

⸻

Response:

{
“balance”: 500,
“lifetime_earned”: 1000,
“lifetime_consumed”: 500
}

⸻

CREDIT HISTORY

API 2

GET /api/v1/credits/history

⸻

Response:

Paginated Ledger Entries

⸻

CREDIT CONSUMPTION SERVICE

Create:

consume_credit()

⸻

Validation:

Sufficient Balance

User Active

Account Not Suspended

⸻

Reject:

INSUFFICIENT_CREDITS

⸻

CREDIT ISSUANCE SERVICE

Create:

issue_credit()

⸻

Validation:

Valid Source

Valid Amount

Audit Required

⸻

CREDIT EXPIRATION

Phase 1:

Disabled

⸻

Future:

Credits may expire.

Architecture must support expiration.

⸻

SUBSCRIPTION MODEL

Purpose:

Platform Operational Revenue

⸻

Paid by:

TRX

BNB

Only

⸻

Plans:

MONTHLY

QUARTERLY

SEMI_ANNUAL

ANNUAL

⸻

SUBSCRIPTION STATUS

ACTIVE

EXPIRED

CANCELLED

PENDING

⸻

SUBSCRIPTION BENEFITS

Monthly Credits

Priority Support

Higher Limits

Advanced Features

Future Benefits

⸻

SUBSCRIPTION API

GET /api/v1/subscription

POST /api/v1/subscription/activate

POST /api/v1/subscription/cancel

⸻

DONATION MODEL

Separate from Subscription.

⸻

Purpose:

Charity Fund

⸻

VNĐ Donations:

Not Platform Revenue

⸻

May generate:

Bonus Credits

Future Phase

⸻

TRUST INTEGRATION

Credit balance affects:

Nothing

⸻

Trust Score and Credits are independent.

⸻

Do NOT increase trust score because of credits.

⸻

ADMIN FEATURES

Admin may:

Grant Credits

Deduct Credits

Suspend Credit Account

⸻

All actions:

Require Audit Logs

⸻

SECURITY REQUIREMENTS

Users cannot:

Modify Balance

Modify Ledger

Transfer Credits

⸻

All balance changes:

Server-side only

⸻

AUDIT EVENTS

CREDIT_ISSUED

CREDIT_CONSUMED

CREDIT_EXPIRED

ADMIN_CREDIT_GRANTED

ADMIN_CREDIT_DEDUCTED

SUBSCRIPTION_ACTIVATED

SUBSCRIPTION_CANCELLED

⸻

FILES TO CREATE

backend/services/credit_service.py

backend/services/subscription_service.py

backend/api/v1/credit/routes.py

backend/api/v1/subscription/routes.py

backend/schemas/credit.py

backend/schemas/subscription.py

backend/repositories/credit_repository.py

⸻

TESTING REQUIREMENTS

Create:

tests/unit/credit/

tests/integration/credit/

tests/security/credit/

⸻

Unit Tests:

Credit Issuance

Credit Consumption

Balance Calculation

Ledger Creation

Subscription Activation

⸻

Integration Tests:

Issue Credits

Consume Credits

View Balance

View History

Activate Subscription

⸻

Security Tests:

Balance Tampering

Ledger Modification

Credit Transfer Attempt

Negative Balance Attack

Double Spend Attempt

⸻

ACCEPTANCE CRITERIA

✓ Credit Account Works

✓ Credit Ledger Works

✓ Credit Issuance Works

✓ Credit Consumption Works

✓ Subscription Works

✓ Audit Logs Created

✓ Ledger Immutable

✓ Tests Pass

⸻

VALIDATION COMMANDS

pytest tests/unit/credit -v

pytest tests/integration/credit -v

pytest tests/security/credit -v

pytest -v

All tests must pass.

⸻

DOCUMENTATION UPDATE

Update:

PROJECT_STATUS_DASHBOARD.md

Change:

Sprint 9

IN PROGRESS

↓

COMPLETED

Update progress percentage.

⸻

COMPLETION REPORT

Create:

SPRINT_9_COMPLETION_REPORT.md

Include:

Summary

Credit Architecture

Ledger Design

Subscription Design

Files Created

APIs Added

Tests Added

Known Issues

Phase 1 Readiness

⸻

GIT COMMIT

Create commit:

[Sprint-9]

Credit System Completed

Push to repository.

⸻

DEFINITION OF DONE

✓ Credit Account Works

✓ Credit Ledger Works

✓ Subscription Works

✓ Audit Logs Created

✓ Tests Pass

✓ Dashboard Updated

✓ Completion Report Created

✓ Git Commit Created

Only then may Sprint 9 be marked COMPLETE.

END OF DOCUMENT