P2PSuperBot — Wallet & Credit Flow

1. Objective

This module is responsible for:

* Wallet registration
* Wallet verification
* Wallet ownership validation
* Credit issuance
* Credit ledger management
* Wallet reputation foundation
* Future TXID relationship network

The objective is to establish trusted blockchain wallet ownership and provide a secure internal credit system.

⸻

2. Supported Wallet Types

Phase 1 supports:

TRON

Network:
TRON
Address:
Txxxxxxxxxxxxxxxxxxxx

⸻

BNB Smart Chain

Network:
BSC
Address:
0x...

⸻

Future:

Ethereum
Bitcoin
Solana
TON
OKX Wallet
Binance Wallet

Not included in Phase 1.

⸻

3. Wallet Categories

Each wallet must belong to one category.

Primary Wallet

Main wallet.

PRIMARY

Rules:

One per network

Example:

1 Primary TRON
1 Primary BSC

⸻

Secondary Wallet

Additional wallet.

SECONDARY

⸻

Exchange Wallet

Wallet controlled by exchange.

Example:

Binance
OKX
Bybit

Category:

EXCHANGE

⸻

Cold Wallet

Long-term storage.

Category:

COLD

⸻

4. Wallet Status

Possible statuses:

PENDING
VERIFICATION_PENDING
VERIFIED
REJECTED
SUSPENDED

⸻

5. Wallet Registration

Command:

/add_wallet

Bot:

Select Network

Options:

TRON
BSC

⸻

User submits:

Wallet Address

⸻

Validation:

Address Format
Duplicate Check
Blacklist Check

⸻

6. Wallet Verification

Wallet ownership must be verified.

Verification proves:

User controls the wallet

⸻

TRON Verification

System generates:

Verification Request

Example:

Verification Wallet:
TSystemWalletXXXX
Minimum:
50 TRX

⸻

User sends:

50 TRX

from the registered wallet.

⸻

System checks:

Sender Address
Receiver Address
Amount
Blockchain Confirmation

⸻

If valid:

Wallet Verified

Status:

VERIFIED

⸻

BSC Verification

Same process.

Example:

Minimum:
0.01 BNB

Configurable.

⸻

7. Wallet Ownership Model

Each wallet linked to:

User ID
Verification Level
Verification Date

⸻

A wallet can belong to:

One verified user

only.

⸻

Duplicate ownership:

DUPLICATE_WALLET_SUSPECTED

requires admin review.

⸻

8. Wallet Visibility

Public display:

TAbc****XYZ
0x12****89EF

⸻

Admins:

Default masked.

Full view requires:

Permission
Reason
Audit Log

⸻

9. Wallet Risk Flags

Reserved for future phases.

Examples:

BLACKLISTED
HIGH_RISK
DISPUTE_ASSOCIATED
UNDER_REVIEW

⸻

10. Credit System

Credits are internal utility units.

Credits are NOT:

Cryptocurrency
Stablecoin
Tradable Asset
Transferable Asset

⸻

Credits only work inside:

P2PSuperBot

⸻

11. Credit Sources

Phase 1:

Wallet Verification

Example:

50 TRX
↓
500 Credits

⸻

TRX Deposit

Example:

100 TRX
↓
1000 Credits

⸻

BNB Deposit

Example:

0.1 BNB
↓
Configured Credits

⸻

Future:

Charity Contribution
Promotion
Affiliate Reward
Admin Reward

⸻

12. Credit Rules

Credits cannot:

Transfer
Trade
Sell
Withdraw
Convert Back

⸻

Credits may only be consumed by system services.

⸻

13. Credit Balance

User command:

/credits

Response:

Current Balance
Total Earned
Total Used

⸻

14. Credit Consumption

Examples:

Check Wallet

1 Credit

⸻

Check User

1 Credit

⸻

Full Reputation Report

5 Credits

⸻

Advanced Analysis

10 Credits

Future configurable.

⸻

15. Credit Ledger

Every change must create a ledger record.

⸻

Fields:

Ledger ID
User ID
Type
Amount
Balance Before
Balance After
Reference ID
Created At

⸻

Types:

WALLET_VERIFICATION
TRX_TOPUP
BNB_TOPUP
CHECK_WALLET_FEE
CHECK_USER_FEE
ADMIN_ADJUSTMENT

⸻

16. Wallet Reputation Foundation

Future phases will track:

Transaction Count
Unique Counterparties
Successful Transactions
Disputes
Wallet Age

⸻

Not implemented in Phase 1.

⸻

17. TXID Submission Foundation

Future feature.

⸻

User command:

/submit_txid

⸻

Stored:

TXID
Sender Wallet
Receiver Wallet
Token
Amount
Network
Timestamp

⸻

Rules:

Only current-day transactions allowed

Historical backfill:

Not allowed

⸻

Purpose:

Relationship Network
Trust Graph
Trade Count

⸻

Not implemented in Phase 1.

⸻

18. Admin Wallet Review

Admin command:

/wallet <user_id>

Can view:

Wallet Count
Wallet Status
Verification History
Credit Balance

⸻

Admin actions:

Approve
Reject
Suspend

⸻

19. Audit Logging

Log:

WALLET_ADDED
WALLET_VERIFIED
WALLET_REJECTED
CREDIT_ADDED
CREDIT_USED
CREDIT_ADJUSTED

⸻

20. Database Tables

Phase 1:

user_wallets
wallet_verifications
credit_accounts
credit_ledger
wallet_audit_logs

⸻

21. Acceptance Criteria

Module is complete when:

✓ User can add wallet

✓ TRON verification works

✓ BSC verification works

✓ Wallet ownership validated

✓ Duplicate detection works

✓ Credit issuance works

✓ Credit balance works

✓ Credit ledger works

✓ Wallet masking works

✓ Admin review works

✓ Audit logs generated

✓ Credits cannot be transferred

✓ Credits cannot be withdrawn

✓ Credits cannot be traded

✓ One wallet belongs to one verified user