PROJECT_MEMORY

Project: P2PSuperBot

Purpose:

This document stores all approved business decisions, architectural decisions, and project conventions.

All AI agents must read this file before implementing any feature.

No approved decision may be changed without explicit approval from the Project Owner.

Project Owner:

Henry Tran

⸻

SECTION 1 — PROJECT VISION

P2PSuperBot is not a trading platform.

P2PSuperBot is a:

Trust Network
Identity Verification Network
Wallet Verification Network
Anti-Scam Infrastructure

The long-term objective is to establish trust between P2P participants.

Trading functionality will be added in future phases.

Trust infrastructure comes first.

⸻

SECTION 2 — PHASE STRATEGY

Phase 1:

Identity Foundation

Includes:

* Registration
* Login
* 2FA
* Profile
* KYC
* eKYC
* Wallet Verification
* Credits
* Admin Review
* Audit Logs

⸻

Phase 2:

Trust Foundation

Planned:

* TXID Tracking
* User Relationships
* Reputation
* Risk Engine
* Trust Score

⸻

Phase 3:

Trading Foundation

Planned:

* P2P Orders
* Escrow
* Disputes
* Merchant Profiles

⸻

SECTION 3 — REGISTRATION DECISIONS

Decision ID:

REG-001

Approved.

Registration requires:

Email Only

No phone number required during registration.

No CCCD required during registration.

⸻

System generates:

User ID
Temporary Password

and sends them via email.

⸻

Decision:

User receives:

Login Guide
2FA Guide
eKYC Guide

during registration.

⸻

SECTION 4 — FIRST LOGIN DECISIONS

Decision ID:

SEC-001

Approved.

First login must:

Force Password Change

⸻

Decision ID:

SEC-002

Approved.

First login must:

Force Google Authenticator Setup

⸻

Decision:

User cannot continue until:

Password Changed
AND
2FA Activated

⸻

Status:

B2_SECURITY_COMPLETED

⸻

SECTION 5 — PASSWORD DECISIONS

Password policy:

Minimum:

12 Characters
1 Uppercase
1 Lowercase
1 Number
1 Special Character

⸻

Passwords:

Never Logged
Never Displayed
Never Stored Plaintext

⸻

Only password hash stored.

⸻

SECTION 6 — 2FA DECISIONS

Approved providers:

Google Authenticator
Microsoft Authenticator
Authy

⸻

Protocol:

RFC6238 TOTP

⸻

Recovery Codes:

Single Use
Stored as Hash

⸻

SECTION 7 — KYC DECISIONS

KYC requires:

CCCD Front
CCCD Back
Selfie

⸻

KYC is:

Manual Verification

⸻

Admin approval required.

⸻

SECTION 8 — EKYC DECISIONS

eKYC is preferred over KYC.

⸻

Trust hierarchy:

EKYC
>
KYC
>
Registered

⸻

User uploads:

PDF Result

from third-party provider.

⸻

System extracts:

Identity Data

from PDF.

⸻

Admin approval required.

⸻

SECTION 9 — PROFILE DECISIONS

Sensitive information must be masked.

Examples:

Email:

hu***@gmail.com

⸻

Phone:

097****677

⸻

CCCD:

079*****789

⸻

Wallet:

TAbc****XYZ

⸻

SECTION 10 — WALLET DECISIONS

Supported Networks:

TRON
BSC

Phase 1 only.

⸻

Wallet Types:

PRIMARY
SECONDARY
EXCHANGE
COLD

⸻

One wallet belongs to:

One Verified User

only.

⸻

Duplicate wallet ownership:

Requires Admin Review

⸻

SECTION 11 — WALLET VERIFICATION DECISIONS

Decision ID:

WAL-001

Approved.

TRON Verification:

50 TRX

minimum.

⸻

Decision ID:

WAL-002

Approved.

BSC Verification:

0.01 BNB

minimum.

⸻

Verification proves:

Wallet Ownership

⸻

SECTION 12 — BANK DECISIONS

Phase 1:

Bank Verification
Not Implemented

⸻

Future Design Approved:

Bank Accounts classified:

Owner Account
Non-Owner Account

⸻

Owner Account:

Name must match:

KYC/eKYC Identity

⸻

Non-Owner Account:

Requires:

Additional eKYC
Relationship Evidence

⸻

SECTION 13 — CREDIT DECISIONS

Credits are:

Internal Utility Units

⸻

Credits are NOT:

Cryptocurrency
Stablecoin
Tradable Asset
Withdrawable Asset

⸻

Credits cannot:

Transfer
Trade
Sell
Withdraw

⸻

Credits only work inside:

P2PSuperBot

⸻

SECTION 14 — CREDIT SOURCES

Wallet Verification:

Example:

50 TRX
↓
500 Credits

⸻

Additional TRX Deposits:

Allowed.

⸻

Additional BNB Deposits:

Allowed.

⸻

SECTION 15 — CHARITY DECISIONS

Approved.

User donations:

Separate From Platform Revenue

⸻

Future:

500,000 VND Donation
↓
Bonus Credits

⸻

Donation funds:

Transferred To Charity Fund

Not platform revenue.

⸻

Community oversight planned.

⸻

SECTION 16 — TXID DECISIONS

Phase 2 feature.

⸻

User may submit:

TXID

to establish transaction relationships.

⸻

Rules:

Only Same-Day Transactions

accepted.

⸻

Historical backfill:

Not Allowed

⸻

Purpose:

Relationship Graph
Trust Graph
Trade Count

⸻

SECTION 17 — ADMIN DECISIONS

Roles:

USER
ADMIN
SUPER_ADMIN

⸻

Admins:

Review verification requests.

⸻

Super Admin:

Manage admins.

⸻

Sensitive data access requires:

Permission
Reason
Audit Log

⸻

SECTION 18 — SECURITY DECISIONS

All sensitive operations:

Private Chat Only

⸻

Never allow in group chat:

Register
Login
Password
2FA
KYC
eKYC
Wallet Verification

⸻

SECTION 19 — AUDIT DECISIONS

Every critical operation:

Must Generate Audit Log

⸻

Retention:

Permanent

⸻

SECTION 20 — ARCHITECTURE DECISIONS

Architecture:

Telegram User
↓
Telegram Bot
↓
FastAPI Backend
↓
Services
↓
Repositories
↓
PostgreSQL

⸻

Redis:

Cache
Queue
Rate Limiting

⸻

Workers:

Email
OCR
PDF Parsing
Wallet Verification
Credits

⸻

SECTION 21 — CODING RULES

Mandatory:

Service Layer
Repository Layer
Security Layer
Worker Layer

⸻

Business logic:

Services Only

⸻

Database access:

Repositories Only

⸻

SECTION 22 — DO NOT CHANGE WITHOUT APPROVAL

The following require explicit approval:

* Registration Flow
* Security Flow
* Verification Hierarchy
* Wallet Verification Amounts
* Credit Rules
* Trust Model
* Role Model
* Architecture

⸻

End Of Memory File