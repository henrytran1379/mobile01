P2PSuperBot — Profile, KYC & eKYC Flow

1. Objective

This module is responsible for:

* Building verified user profiles
* Identity verification
* KYC management
* eKYC management
* Trust foundation
* Admin verification workflow
* Future wallet and bank verification linkage

The objective is to ensure every verified user has a trusted digital identity before participating in future P2P activities.

⸻

2. Verification Levels

Every user belongs to one verification level.

Level 0 — Registered

Requirements:

Email Verified
Password Changed
2FA Activated

Status:

REGISTERED

Capabilities:

View Profile
Update Basic Profile
Submit KYC
Submit eKYC

⸻

Level 1 — KYC Verified

Requirements:

CCCD Front
CCCD Back
Selfie
Admin Approval

Status:

KYC_VERIFIED

⸻

Level 2 — eKYC Verified

Requirements:

Third Party eKYC
PDF Result
Admin Approval

Status:

EKYC_VERIFIED

eKYC always has higher trust value than manual KYC.

⸻

3. Profile Structure

Each user profile contains:

Core Identity

User ID
Telegram ID
Telegram Username
Email

⸻

Personal Information

Full Name
Date of Birth
Gender
Nationality

⸻

Government Identity

CCCD Number
Issue Date
Issue Place
Expiry Date

⸻

Verification Status

KYC Status
eKYC Status
Verification Level
Verified At
Verified By

⸻

Reputation Foundation

Reserved for future phases:

Trust Score
Reputation Score
Risk Score

Not implemented in Phase 1.

⸻

4. KYC Path

Manual verification path.

⸻

Required Documents

Front Side

CCCD Front Image

⸻

Back Side

CCCD Back Image

⸻

Selfie

Current Selfie

⸻

Upload Flow

User:

/kyc

Bot:

Upload CCCD Front

User uploads.

Bot:

Upload CCCD Back

User uploads.

Bot:

Upload Selfie

User uploads.

⸻

OCR Extraction

System attempts to extract:

Full Name
CCCD Number
DOB
Gender
Issue Date
Expiry Date

⸻

Review Status

KYC_PENDING_REVIEW

⸻

5. eKYC Path

Preferred verification path.

⸻

Third-Party Provider

User completes eKYC externally.

System provides:

eKYC Guide
Recommended Providers
PDF Export Instructions

during B1 registration email.

⸻

Upload

User:

/ekyc

Bot:

Upload eKYC PDF

⸻

Processing

System:

Store PDF
Parse PDF
Extract Data
Generate Review Record

⸻

Extracted Fields

Examples:

Full Name
DOB
Nationality
Address
ID Number
Verification Result
Provider Reference
Provider Score
Verification Date

⸻

Review Status

EKYC_PENDING_REVIEW

⸻

6. Trust Hierarchy

Trust ranking:

eKYC Verified
>
KYC Verified
>
Registered Only

Example:

Level 2 = eKYC Verified
Level 1 = KYC Verified
Level 0 = Registered

⸻

7. User Visible Verification Badge

Examples:

🟢 eKYC Verified
🟡 KYC Verified
⚪ Registered Only

⸻

8. Profile Visibility Rules

User Profile:

Default display:

User ID
Verification Level
Verification Badge
Verified Since

⸻

Sensitive information must be masked.

⸻

Email

Display:

hu***@gmail.com

⸻

Phone

Display:

097****677

⸻

CCCD

Display:

079*****789

⸻

Wallet

Display:

TAbc****XYZ

⸻

9. Profile Update Rules

Editable:

Telegram Username
Display Name
Avatar

⸻

Restricted:

Full Name
DOB
CCCD

Require:

New KYC Review

if changed.

⸻

10. Duplicate Detection

System checks:

Email
Telegram ID
CCCD Number

to prevent duplicate identities.

⸻

Possible status:

DUPLICATE_SUSPECTED

⸻

11. Admin Review Flow

Admin receives:

Review Queue

⸻

Review Actions

Approve

Result:

KYC_VERIFIED

or

EKYC_VERIFIED

⸻

Reject

Admin must provide:

Reason

Example:

Image Blurry
Data Mismatch
Document Invalid

⸻

Re-Submit

User may:

Re-upload

after rejection.

⸻

12. Profile Query

User command:

/profile

Returns:

User ID
Verification Badge
Verification Level
Verification Status
Created Date
Last Verification Date

⸻

13. Admin Profile Lookup

Admin:

/user <user_id>

Can view:

Verification Status
Review History
Wallet Count
Credit Balance

Sensitive data remains masked by default.

⸻

14. Audit Logging

Log:

KYC_SUBMITTED
KYC_APPROVED
KYC_REJECTED
EKYC_SUBMITTED
EKYC_APPROVED
EKYC_REJECTED
PROFILE_UPDATED

⸻

15. File Storage

Store separately:

CCCD Front
CCCD Back
Selfie
eKYC PDF

Recommended:

Encrypted Storage

⸻

Never Store

Raw OCR Logs
Temporary Parsed Files

after processing.

⸻

16. Database Tables

Phase 1:

user_profiles
kyc_submissions
ekyc_submissions
verification_reviews
user_documents
audit_logs

⸻

17. Status Model

REGISTERED
KYC_PENDING_REVIEW
KYC_VERIFIED
KYC_REJECTED
EKYC_PENDING_REVIEW
EKYC_VERIFIED
EKYC_REJECTED
DUPLICATE_SUSPECTED

⸻

18. Acceptance Criteria

Module is complete when:

✓ User can submit KYC

✓ User can upload CCCD Front

✓ User can upload CCCD Back

✓ User can upload Selfie

✓ OCR extraction works

✓ User can upload eKYC PDF

✓ PDF parsing works

✓ Admin review works

✓ Approve/Reject works

✓ Verification badges displayed

✓ Sensitive data masked

✓ Audit logs generated

✓ Verification level correctly assigned

✓ Profile query works

✓ Duplicate detection works