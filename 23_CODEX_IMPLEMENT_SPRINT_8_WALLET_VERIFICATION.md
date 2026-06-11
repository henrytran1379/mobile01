CODEX_IMPLEMENT_SPRINT_8_WALLET_VERIFICATION

Role:

You are the Primary Implementation Agent for P2PSuperBot.

Implement Sprint 8 exactly according to approved specifications.

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
6. 05_WALLET_CREDIT_FLOW.md
7. 06_ADMIN_REVIEW_FLOW.md
8. 08_API_SERVICE_DESIGN_PHASE1.md
9. 14_CODEX_STARTUP_PROMPT.md

Review Sprint 1–7 implementation before starting.

⸻

SPRINT INFORMATION

Sprint:

Sprint 8

Wallet Verification Module

Goal:

Implement complete wallet ownership verification workflow.

⸻

BUSINESS OBJECTIVE

Prove:

Verified User

↓

Owns

↓

Blockchain Wallet

This is the foundation of:

Trust Network

TXID Network

Reputation Graph

Anti-Scam System

Merchant Verification

⸻

TRUST MODEL INTEGRATION

Before Wallet Verification:

Level 3

EKYC VERIFIED

Trust Score:

500

⸻

After Wallet Verification:

Level 4

WALLET VERIFIED

Trust Score:

700

Badge:

WALLET VERIFIED

⸻

SUPPORTED NETWORKS

Phase 1:

TRON (TRC20)

BSC (BEP20)

⸻

Future:

Ethereum

Solana

TON

Bitcoin

⸻

DATABASE TABLES USED

Use:

user_wallets

wallet_verifications

credit_accounts

credit_ledger

audit_logs

trust_scores

verification_reviews

⸻

WALLET TYPES

Supported:

PRIMARY

SECONDARY

EXCHANGE

COLD

⸻

One wallet may belong to:

One verified user only.

⸻

WALLET STATUS

PENDING

VERIFYING

VERIFIED

REJECTED

SUSPENDED

⸻

WALLET VERIFICATION RULES

TRON:

Minimum:

50 TRX

⸻

BSC:

Minimum:

0.01 BNB

⸻

Verification transaction proves:

Wallet Ownership

⸻

WALLET FLOW

User

↓

Add Wallet

↓

System Generates Verification Reference

↓

User Transfers Required Amount

↓

Blockchain Verification

↓

Admin Review (if needed)

↓

Wallet Verified

↓

Credits Issued

↓

Trust Updated

⸻

API 1

Add Wallet

POST /api/v1/wallets

⸻

Request:

{
“network”: “TRON”,
“wallet_address”: “…”
}

⸻

Response:

{
“wallet_id”: “…”,
“status”: “PENDING”
}

⸻

WALLET VALIDATION

Validate:

Address Format

Network Compatibility

Checksum (if applicable)

Duplicate Ownership

⸻

Reject:

Invalid Address

Unsupported Network

Duplicate Verified Wallet

⸻

API 2

Initiate Verification

POST /api/v1/wallets/{wallet_id}/verify

⸻

Response:

{
“verification_reference”: “…”,
“required_amount”: “50”,
“network”: “TRON”
}

⸻

VERIFICATION REFERENCE

Generate:

Unique Reference

Example:

P2P-WALLET-8A9F31

⸻

Store:

wallet_verifications

⸻

BLOCKCHAIN LISTENER

Create:

Blockchain Verification Service

⸻

Monitor:

TRON Wallet

BSC Wallet

⸻

Detect:

Incoming Verification Transaction

⸻

Validate:

Amount

Network

Reference

Sender Address

⸻

TRANSACTION MATCHING

Must Match:

Wallet Address

Verification Amount

Verification Window

Reference

⸻

If valid:

Verification Passed

⸻

VERIFICATION WINDOW

Default:

24 Hours

⸻

Expired:

Status:

EXPIRED

⸻

CREDIT ISSUANCE

TRON Verification:

50 TRX

↓

500 Credits

⸻

BNB Verification:

Configurable

⸻

Credits:

Non-transferable

Non-withdrawable

Internal Use Only

⸻

CREDIT LEDGER

Create entry:

WALLET_VERIFICATION_REWARD

⸻

Metadata:

Wallet

Network

Transaction Hash

⸻

TRUST UPDATE

When Wallet Verified:

Level:

4

⸻

Trust Score:

700

⸻

Badge:

WALLET VERIFIED

⸻

Create:

TRUST_EVENT

⸻

API 3

Wallet Status

GET /api/v1/wallets/{wallet_id}

⸻

Response:

{
“status”: “VERIFIED”,
“network”: “TRON”,
“verified_at”: “…”
}

⸻

API 4

My Wallets

GET /api/v1/wallets

⸻

Response:

Wallet List

Status

Network

Verification Date

Type

⸻

DUPLICATE DETECTION

Check:

Wallet Already Verified

Wallet Linked To Another User

Wallet Previously Banned

⸻

Flag:

DUPLICATE_WALLET

⸻

Require:

Admin Review

⸻

ADMIN REVIEW

Queue:

WALLET_REVIEW

⸻

Admin Sees:

Wallet

Owner

Verification Data

Transaction Hash

Duplicate Flags

History

⸻

BLOCKCHAIN ABSTRACTION

Create:

IBlockchainProvider

⸻

Implement:

TronProvider

BscProvider

⸻

Future:

EthereumProvider

SolanaProvider

TonProvider

⸻

Do not hardcode networks.

⸻

SECURITY REQUIREMENTS

Only owner may manage wallet.

All wallet access logged.

Never expose:

Internal verification references publicly.

⸻

AUDIT EVENTS

WALLET_ADDED

WALLET_VERIFICATION_STARTED

WALLET_VERIFIED

WALLET_REJECTED

WALLET_DUPLICATE_FLAGGED

CREDIT_ISSUED

⸻

FILES TO CREATE

backend/services/wallet_service.py

backend/services/blockchain_verification_service.py

backend/api/v1/wallet/routes.py

backend/schemas/wallet.py

backend/repositories/wallet_repository.py

backend/providers/blockchain/base_provider.py

backend/providers/blockchain/tron_provider.py

backend/providers/blockchain/bsc_provider.py

⸻

TESTING REQUIREMENTS

Create:

tests/unit/wallet/

tests/integration/wallet/

tests/security/wallet/

⸻

Unit Tests:

Address Validation

Reference Generation

Credit Calculation

Trust Upgrade

Duplicate Detection

⸻

Integration Tests:

Add Wallet

Verify Wallet

Credit Issuance

Trust Update

Admin Review

⸻

Security Tests:

Unauthorized Access

Wallet Hijacking

Duplicate Wallet Attack

Reference Reuse

Verification Replay Attack

⸻

ACCEPTANCE CRITERIA

✓ Wallet Added

✓ Verification Started

✓ Blockchain Detection Works

✓ Verification Works

✓ Credits Issued

✓ Trust Updated

✓ Duplicate Detection Works

✓ Admin Review Works

✓ Audit Logs Created

✓ Unit Tests Pass

✓ Integration Tests Pass

✓ Security Tests Pass

⸻

VALIDATION COMMANDS

pytest tests/unit/wallet -v

pytest tests/integration/wallet -v

pytest tests/security/wallet -v

pytest -v

All tests must pass.

⸻

DOCUMENTATION UPDATE

Update:

PROJECT_STATUS_DASHBOARD.md

Change:

Sprint 8

IN PROGRESS

↓

COMPLETED

Update progress percentage.

⸻

COMPLETION REPORT

Create:

SPRINT_8_COMPLETION_REPORT.md

Include:

Summary

Blockchain Architecture

Wallet Verification Design

Credit Issuance Design

Files Created

APIs Added

Tests Added

Trust Model Impact

Known Issues

Sprint 9 Readiness

⸻

GIT COMMIT

Create commit:

[Sprint-8]

Wallet Verification Module Completed

Push to repository.

⸻

DEFINITION OF DONE

✓ Wallet Verification Works

✓ Blockchain Listener Works

✓ Credits Issued

✓ Trust Updated

✓ Audit Logs Created

✓ Tests Pass

✓ Dashboard Updated

✓ Completion Report Created

✓ Git Commit Created

Only then may Sprint 8 be marked COMPLETE.

END OF DOCUMENT