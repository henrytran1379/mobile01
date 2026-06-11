TRUST_VERIFICATION_MODEL

Document ID: TVM-001

Version: 1.0

Status: Approved

Project: P2PSuperBot

Owner: Henry Tran

⸻

1. PURPOSE

This document defines:

* Verification Levels
* Trust Levels
* Trust Scores
* Verification Badges
* Feature Permissions
* Risk Classification

for the entire P2PSuperBot ecosystem.

All future modules must comply with this model.

⸻

2. CORE PRINCIPLE

P2PSuperBot is a Trust Network.

Trust is earned through verification.

More verification

Higher trust

Higher trust

More permissions

⸻

3. TRUST LEVELS

LEVEL 0

Anonymous

Status:

No Account

Requirements:

None

Trust Score:

0

Badge:

NONE

Permissions:

View Public Information Only

⸻

LEVEL 1

Registered User

Status:

Registration Completed

Requirements:

✓ Email Verified

✓ Password Changed

✓ 2FA Enabled

Trust Score:

100

Badge:

REGISTERED

Color:

Gray

Permissions:

Profile Access
Wallet Submission
KYC Submission

⸻

LEVEL 2

KYC Verified

Requirements:

✓ Level 1

✓ CCCD Front

✓ CCCD Back

✓ Selfie

✓ Admin Approved

Trust Score:

300

Badge:

KYC VERIFIED

Color:

Blue

Permissions:

Wallet Verification
Transaction Recording
Community Participation

⸻

LEVEL 3

eKYC Verified

Requirements:

✓ Level 1

✓ Third Party eKYC PDF

✓ Admin Approved

Trust Score:

500

Badge:

EKYC VERIFIED

Color:

Green

Permissions:

Higher Visibility
Priority Verification
Advanced Features

⸻

LEVEL 4

Wallet Verified

Requirements:

✓ Level 2 OR Level 3

✓ Wallet Ownership Verified

Trust Score:

700

Badge:

WALLET VERIFIED

Color:

Cyan

Permissions:

Wallet Reputation
Transaction Relationship Building
Trust Network Participation

⸻

LEVEL 5

Bank Verified

Future Phase

Requirements:

✓ Identity Match

✓ Bank Ownership Verification

Trust Score:

900

Badge:

BANK VERIFIED

Color:

Purple

Permissions:

Advanced Trust Features

⸻

LEVEL 6

Merchant Verified

Future Phase

Requirements:

✓ Long Activity History

✓ High Reputation

✓ Manual Approval

Trust Score:

1200

Badge:

MERCHANT VERIFIED

Color:

Gold

Permissions:

Merchant Features
Community Endorsement
Escrow Access

⸻

4. TRUST SCORE MODEL

Trust Score is cumulative.

Base Score:

Registered:
100

KYC:
+200

eKYC:
+400

Wallet Verified:
+200

Bank Verified:
+200

Merchant Verified:
+300

⸻

5. ACTIVITY SCORE

Additional score may be earned from activity.

Examples:

Transaction History:
+1 each

Successful Trade:
+2 each

Verified Counterparty:
+3 each

Community Endorsement:
+5 each

⸻

Maximum activity score:

500

⸻

6. RISK SCORE

Separate from Trust Score.

Trust Score:

Higher = Better

Risk Score:

Higher = Worse

Range:

0 - 100

⸻

Risk Factors:

Chargebacks

Disputes

Fraud Reports

Fake Documents

Wallet Abuse

Ban History

⸻

7. VERIFICATION BADGES

Displayed:

Profile

Wallet

Search Results

Transaction History

Community Rankings

⸻

Badges:

REGISTERED
KYC VERIFIED
EKYC VERIFIED
WALLET VERIFIED
BANK VERIFIED
MERCHANT VERIFIED

⸻

8. PROFILE VISIBILITY

Public profile shows:

User Code

Trust Level

Trust Score

Badges

Wallet Count

Transaction Count

Join Date

⸻

Never show:

Password

2FA Secret

Recovery Codes

CCCD Number

Full Email

Full Phone

⸻

9. FEATURE ACCESS MATRIX

LEVEL 1

Can:

✓ Submit KYC

✓ Submit Wallet

Cannot:

✗ Create Merchant Profile

⸻

LEVEL 2

Can:

✓ Wallet Verification

✓ TXID Submission

⸻

LEVEL 3

Can:

✓ Priority Verification

✓ Enhanced Search Ranking

⸻

LEVEL 4

Can:

✓ Wallet Reputation

✓ Trust Network Participation

⸻

LEVEL 5

Can:

✓ Bank-linked Trust Features

⸻

LEVEL 6

Can:

✓ Merchant Marketplace

✓ Escrow

✓ Commercial Features

⸻

10. TRUST RANKING

Categories:

Bronze

Silver

Gold

Platinum

Diamond

⸻

Bronze:

0-299

Silver:

300-599

Gold:

600-899

Platinum:

900-1199

Diamond:

1200+

⸻

11. COMMUNITY REPUTATION

Future Phase

Sources:

Transaction Confirmations

Counterparty Ratings

Dispute Outcomes

Community Endorsements

⸻

12. TXID RELATIONSHIP MODEL

Future Phase

Each verified TXID creates:

Relationship Edge

Between:

Sender Wallet

Receiver Wallet

⸻

Trust Graph grows over time.

⸻

13. SEARCH PRIORITY

Higher Trust Score:

Higher Search Ranking

Higher Visibility

Higher Community Confidence

⸻

14. FRAUD PROTECTION

Automatic Review Trigger:

Multiple Wallet Changes

Multiple Failed Verifications

Document Mismatch

Fake Identity Detection

High Risk Score

⸻

15. ADMIN OVERRIDE

Admins may:

Approve

Reject

Suspend

Review

⸻

All overrides require:

Reason

Audit Log

Timestamp

Admin ID

⸻

16. DATABASE REQUIREMENTS

Future tables:

trust_scores

risk_scores

trust_events

user_relationships

wallet_relationships

community_ratings

merchant_profiles

⸻

17. API REQUIREMENTS

Future APIs:

GET /trust/profile

GET /trust/score

GET /trust/risk

GET /trust/history

GET /trust/badges

⸻

18. SUCCESS CRITERIA

A user’s trust level must be:

Deterministic

Auditable

Transparent

Reproducible

Not manually manipulated without audit trail.

END OF DOCUMENT