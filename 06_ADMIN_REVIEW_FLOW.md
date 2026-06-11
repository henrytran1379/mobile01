P2PSuperBot — Admin Review Flow

1. Objective

This module is responsible for:

* User verification review
* KYC review
* eKYC review
* Wallet review
* Security oversight
* Credit adjustment review
* Audit and compliance controls

The objective is to ensure that all sensitive actions are reviewed and traceable.

⸻

2. Role Hierarchy

Phase 1 supports:

Super Admin

Highest privilege.

Can:

Manage Admins
View All Data
View Full Identity Data
Review KYC/eKYC
Review Wallets
Adjust Credits
Suspend Users
Unlock Users
View Audit Logs
System Configuration

⸻

Admin

Operational role.

Can:

Review KYC
Review eKYC
Review Wallet Verification
Review User Profile
Approve
Reject
Suspend Wallet
View Masked Information

Cannot:

Create Admin
Delete Admin
View System Secrets
Modify Core Settings

⸻

User

Can:

Register
Login
Submit KYC
Submit eKYC
Add Wallet
View Own Data

⸻

3. Review Queue

Admin dashboard contains:

Pending KYC
Pending eKYC
Pending Wallet Verification
Duplicate Suspects
Security Alerts

⸻

4. KYC Review

Review Item:

User ID
Masked Email
CCCD Front
CCCD Back
Selfie
OCR Result
Submission Date

⸻

Approve

Result:

KYC_VERIFIED

Notification:

Your KYC has been approved.

⸻

Reject

Admin must provide reason.

Examples:

Image blurry
Invalid document
Face mismatch
Expired document

Result:

KYC_REJECTED

⸻

5. eKYC Review

Review Item:

User ID
eKYC PDF
Parsed Data
Provider Result
Verification Date

⸻

Approve

Result:

EKYC_VERIFIED

⸻

Reject

Reason required.

Examples:

Invalid PDF
Provider failure
Data mismatch

⸻

6. Wallet Review

Review Item:

User ID
Wallet Address
Network
Verification TXID
Verification Amount
Verification Date

⸻

Admin verifies:

Sender Address
Receiver Address
Amount
Network

⸻

Approve

Result:

WALLET_VERIFIED

Credits issued automatically.

⸻

Reject

Examples:

Wrong Sender
Wrong Amount
Failed Verification

⸻

7. Duplicate Detection Review

System automatically flags:

Duplicate Email
Duplicate CCCD
Duplicate Wallet
Suspicious Similarity

Status:

DUPLICATE_SUSPECTED

⸻

Admin actions:

Confirm Duplicate
Dismiss Alert
Escalate

⸻

8. User Lookup

Admin command:

/user <user_id>

Returns:

User ID
Verification Status
Wallet Count
Credit Balance
Account Status

Sensitive fields masked.

⸻

9. Full Information Access

Default:

Masked Only

Examples:

Email:
hu***@gmail.com
CCCD:
079*****789
Wallet:
TAbc****XYZ

⸻

To reveal full information:

Requirements:

Admin Permission
Reason
2FA Verification
Audit Log

⸻

10. Credit Adjustment

Phase 1 allows manual adjustment.

Types:

Add Credits
Deduct Credits
Correction
Compensation

⸻

Required:

Reason
Reference
Admin ID

⸻

All actions recorded.

⸻

11. Account Suspension

Admin can suspend:

User Account
Wallet

Reasons:

Fraud Investigation
Duplicate Identity
Security Risk
Compliance Review

Status:

SUSPENDED

⸻

12. Security Alerts

System generates alerts:

Multiple Failed Logins
Multiple Wallet Attempts
Duplicate CCCD
Duplicate Wallet
Suspicious Activity

Review Queue:

SECURITY_ALERT_QUEUE

⸻

13. Admin Actions Requiring 2FA

Mandatory:

Approve eKYC
Reveal Full Data
Adjust Credits
Suspend User
Unsuspend User
Create Admin
Delete Admin

⸻

14. Super Admin Functions

Only Super Admin can:

Create Admin
Disable Admin
Reset Admin 2FA
View Full Audit History
System Maintenance
Manage Roles

⸻

15. Audit Logging

Every admin action must be logged.

Fields:

Audit ID
Admin ID
Action
Target User
Reason
Timestamp
IP Address

⸻

Examples:

KYC_APPROVED
EKYC_REJECTED
WALLET_APPROVED
WALLET_REJECTED
CREDIT_ADJUSTMENT
USER_SUSPENDED
DATA_REVEALED

⸻

16. Audit Retention

Minimum:

5 years

Recommended:

Permanent

⸻

17. Database Tables

Phase 1:

admin_users
admin_roles
review_queue
review_decisions
security_alerts
audit_logs

⸻

18. Acceptance Criteria

Module is complete when:

✓ Admin can review KYC

✓ Admin can review eKYC

✓ Admin can review Wallet Verification

✓ Duplicate Detection Review works

✓ Credit Adjustment works

✓ User Suspension works

✓ Full Data Access requires reason

✓ Full Data Access logged

✓ Admin 2FA enforced

✓ Super Admin role works

✓ Audit logs generated for all actions

✓ Security Alert Queue works