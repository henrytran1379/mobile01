P2PSuperBot — Phase 1 Master Specification

Version: 1.0

Status: Approved

Author: Henry Tran

Purpose:

This document serves as the single source of truth (SSOT) for Phase 1 implementation.

All Codex agents, developers, reviewers, and testers must use this document as the primary reference before consulting detailed specifications.

⸻

1. Phase 1 Objective

Phase 1 establishes the trust foundation of P2PSuperBot.

The objective is to build:

* User Registration
* Secure Authentication
* Google Authenticator 2FA
* User Profile Management
* KYC Verification
* eKYC Verification
* Wallet Verification
* Credit System
* Admin Review System
* Audit Logging

No P2P Trading functionality is included in Phase 1.

No Escrow functionality is included in Phase 1.

No Reputation Scoring is included in Phase 1.

No Dispute Management is included in Phase 1.

Phase 1 only builds trusted identities and trusted wallets.

⸻

2. Core Design Principles

Security First

Every sensitive operation must require:

* Authentication
* Authorization
* Audit Logging

⸻

Privacy First

Personal information must be masked.

Examples:

Email:

hu***@gmail.com

Phone:

097****677

CCCD:

079*****789

Wallet:

TAbc****XYZ

⸻

Trust Before Trading

Users must first establish trust through:

* Registration
* Security Activation
* KYC/eKYC
* Wallet Verification

Only after future phases will users be allowed to participate in P2P activities.

⸻

3. User Lifecycle

Step 1

Registration

User submits:

Email

System sends:

* User ID
* Temporary Password
* Activation Instructions
* Google Authenticator Guide
* eKYC Guide

Status:

WAITING_FIRST_LOGIN

⸻

Step 2

First Login

User logs in using:

* User ID or Email
* Temporary Password

System forces:

* Password Change
* Google Authenticator Setup

Status:

B2_SECURITY_COMPLETED

⸻

Step 3

Profile Setup

User may update:

* Display Name
* Telegram Username
* Avatar

Restricted identity fields require re-verification.

⸻

Step 4

KYC or eKYC

User chooses:

KYC

Upload:

* CCCD Front
* CCCD Back
* Selfie

System performs OCR.

Admin reviews.

⸻

eKYC

User completes third-party eKYC.

User uploads PDF.

System parses PDF.

Admin reviews.

⸻

Step 5

Wallet Verification

User adds:

* TRON Wallet
* BSC Wallet

User verifies ownership by sending blockchain verification transaction.

Credits issued after verification.

⸻

4. Verification Levels

Level 0

REGISTERED

Requirements:

* Email Verified
* Password Changed
* 2FA Enabled

⸻

Level 1

KYC_VERIFIED

Requirements:

* CCCD
* Selfie
* Admin Approval

⸻

Level 2

EKYC_VERIFIED

Requirements:

* Third-party eKYC
* PDF Validation
* Admin Approval

Trust Ranking:

EKYC_VERIFIED

KYC_VERIFIED

REGISTERED

⸻

5. Authentication Model

Supported Login:

* Email
* User ID

Required:

* Password

Optional:

* Google Authenticator

Mandatory after first login.

⸻

Password Rules:

Minimum:

* 12 Characters
* 1 Uppercase
* 1 Lowercase
* 1 Number
* 1 Special Character

⸻

Account Lock:

5 failed attempts

Lock:

15 minutes

⸻

6. Google Authenticator

Supported:

* Google Authenticator
* Microsoft Authenticator
* Authy

Protocol:

RFC6238 TOTP

⸻

Features:

* QR Setup
* Verification
* Recovery Codes

Recovery Codes:

Single-use only.

Stored as hashes.

⸻

7. Profile System

Stores:

* Personal Information
* Identity Information
* Verification Status

Visible:

* User ID
* Verification Badge
* Verification Level

Sensitive data remains masked.

⸻

8. KYC System

Required:

* CCCD Front
* CCCD Back
* Selfie

OCR extracts:

* Full Name
* CCCD Number
* DOB
* Gender
* Issue Date

Admin reviews result.

⸻

9. eKYC System

User uploads:

eKYC PDF

System extracts:

* Full Name
* Identity Number
* Verification Result
* Provider Information

Admin reviews result.

⸻

10. Wallet System

Supported Networks:

* TRON
* BSC

Wallet Categories:

* Primary
* Secondary
* Exchange
* Cold

One wallet may belong to only one verified user.

Duplicate ownership requires review.

⸻

11. Wallet Verification

TRON Example:

User sends:

50 TRX

to verification address.

System validates:

* Sender
* Receiver
* Amount
* Confirmation

Status:

VERIFIED

Credits issued automatically.

⸻

12. Credit System

Credits are internal utility units.

Credits are:

* Non-transferable
* Non-tradable
* Non-withdrawable

Credits only function inside P2PSuperBot.

⸻

Credit Sources:

* Wallet Verification
* TRX Deposit
* BNB Deposit
* Future Promotions

⸻

Credit Usage:

* Wallet Checks
* User Checks
* Reputation Reports
* Future Services

⸻

13. Admin Model

Roles:

USER

ADMIN

SUPER_ADMIN

⸻

Admin Functions:

* Review KYC
* Review eKYC
* Review Wallet Verification
* Manage Review Queue

⸻

Super Admin Functions:

* Create Admin
* Disable Admin
* Reveal Full Information
* Configure System

⸻

14. Data Access Policy

Default:

Masked View Only

Full Information Access requires:

* Permission
* Reason
* Audit Log
* 2FA Verification

⸻

15. Audit Logging

Every critical operation must generate an audit record.

Examples:

* Login
* Password Change
* 2FA Setup
* KYC Approval
* Wallet Verification
* Credit Adjustment
* Admin Actions

Retention:

Permanent

⸻

16. Database Modules

Phase 1 Tables:

users

user_security

registration_sessions

user_sessions

recovery_codes

user_profiles

user_identity_documents

kyc_submissions

ekyc_submissions

verification_reviews

user_wallets

wallet_verifications

credit_accounts

credit_ledger

admin_users

admin_roles

review_queue

security_alerts

audit_logs

user_documents

⸻

17. API Modules

Phase 1 APIs:

auth

profile

kyc

ekyc

wallet

credits

admin

health

⸻

18. Telegram Bot Modules

Public:

/start
/help
/register
/login
/reset_password

⸻

User:

/2fa_setup
/profile
/profile_update
/kyc
/ekyc
/wallets
/add_wallet
/credits
/logout

⸻

Admin:

/review_queue
/review
/user
/wallet
/security_alerts

⸻

Super Admin:

/create_admin
/disable_admin
/audit_logs

⸻

19. Architecture

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

Redis provides:

* Cache
* Session Storage
* Rate Limiting
* Queue Management

Workers provide:

* Email Processing
* OCR
* PDF Parsing
* Wallet Verification
* Credit Processing

⸻

20. Phase 1 Completion Criteria

Phase 1 is complete when:

✓ Registration Works

✓ First Login Works

✓ Password Change Works

✓ Google Authenticator Works

✓ Recovery Codes Work

✓ Profile Works

✓ KYC Works

✓ eKYC Works

✓ Wallet Verification Works

✓ Credits Work

✓ Admin Review Works

✓ Audit Logs Work

✓ Database Complete

✓ API Complete

✓ Telegram Bot Complete

✓ Integration Tests Pass

✓ Security Tests Pass

✓ Production Deployment Ready

End of Master Specification