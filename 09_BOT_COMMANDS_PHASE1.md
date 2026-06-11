P2PSuperBot — Bot Commands Phase 1

1. Objective

This document defines all Telegram Bot commands available in Phase 1.

Phase 1 scope:

Register
Login
2FA
Profile
KYC
eKYC
Wallet
Credits
Admin Review

All sensitive operations must be performed in:

Private Chat Only

⸻

2. Command Categories

Public Commands

Available before login.

/start
/help
/register
/login
/reset_password

⸻

User Commands

Available after login.

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

Admin Commands

/review_queue
/review
/user
/wallet
/security_alerts

⸻

Super Admin Commands

/create_admin
/disable_admin
/audit_logs

⸻

3. Start Command

Command:

/start

Response:

Welcome to P2PSuperBot
Verification & Trust Network
Available Commands:
/register
/login
/help

⸻

4. Help Command

Command:

/help

Response:

Registration
Login
Profile
Wallet
Credits
Support

Dynamic according to role.

⸻

5. Register Command

Command:

/register

Bot:

Please enter your email address.

⸻

User:

user@gmail.com

⸻

Bot:

Registration request received.
Check your email.
You will receive:
User ID
Temporary Password
2FA Activation Guide
eKYC Guide

⸻

Backend:

POST /api/v1/auth/register

⸻

6. Login Command

Command:

/login

⸻

Bot:

Enter Email or User ID

⸻

User enters.

Bot:

Enter Password

⸻

Backend:

POST /api/v1/auth/login

⸻

Possible Responses

First Login

Password change required.

⸻

2FA Required

Enter 2FA Code.

⸻

Success

Login successful.

⸻

7. Password Reset

Command:

/reset_password

⸻

Bot:

Enter registered email.

⸻

Backend:

POST /api/v1/auth/reset-password

⸻

Response:

Password reset email sent.

⸻

8. 2FA Setup

Command:

/2fa_setup

⸻

Bot:

Generating QR Code...

⸻

Backend:

POST /api/v1/auth/2fa/setup

⸻

Bot displays:

QR Code
Instructions
Enter first code.

⸻

User:

123456

⸻

Backend:

POST /api/v1/auth/2fa/verify

⸻

Success:

2FA activated successfully.

⸻

9. Profile Command

Command:

/profile

⸻

Backend:

GET /api/v1/profile

⸻

Response:

User ID
Verification Level
Verification Badge
Email (masked)
Wallet Count
Credit Balance

⸻

10. Profile Update

Command:

/profile_update

⸻

Editable:

Display Name
Avatar
Telegram Username

⸻

Backend:

PUT /api/v1/profile

⸻

11. KYC Command

Command:

/kyc

⸻

Bot:

Upload CCCD Front

⸻

User uploads.

Bot:

Upload CCCD Back

⸻

User uploads.

Bot:

Upload Selfie

⸻

Backend:

POST /api/v1/kyc/submit

⸻

Response:

KYC submitted.
Status:
Pending Review

⸻

12. eKYC Command

Command:

/ekyc

⸻

Bot:

Upload eKYC PDF

⸻

Backend:

POST /api/v1/ekyc/upload

⸻

Response:

eKYC submitted.
Status:
Pending Review

⸻

13. Wallet List

Command:

/wallets

⸻

Backend:

GET /api/v1/wallets

⸻

Response:

Primary Wallet
Secondary Wallets
Verification Status

⸻

14. Add Wallet

Command:

/add_wallet

⸻

Bot:

Select Network:
1. TRON
2. BSC

⸻

User selects.

Bot:

Enter Wallet Address.

⸻

Backend:

POST /api/v1/wallets

⸻

Bot:

Wallet added.
Verification required.

⸻

15. Wallet Verification

Bot:

Send:
50 TRX
to:
Txxxxxxxxxxxxx

or

0.01 BNB

⸻

Worker validates.

⸻

Success:

Wallet verified.
500 credits added.

⸻

16. Credits

Command:

/credits

⸻

Backend:

GET /api/v1/credits/balance

⸻

Response:

Balance:
500
Earned:
500
Used:
0

⸻

17. Logout

Command:

/logout

⸻

Backend:

Invalidate Session

⸻

Response:

Logged out successfully.

⸻

18. Admin Review Queue

Command:

/review_queue

⸻

Response:

Pending KYC
Pending eKYC
Pending Wallet Verification
Security Alerts

⸻

19. Admin Review

Command:

/review <review_id>

⸻

Response:

Review Details
Approve
Reject

⸻

Admin chooses.

⸻

20. User Lookup

Command:

/user <user_id>

⸻

Response:

User ID
Verification Status
Wallet Count
Credit Balance
Email (masked)
CCCD (masked)

⸻

21. Wallet Lookup

Command:

/wallet <user_id>

⸻

Response:

Wallet Count
Verification Status
Network
Masked Addresses

⸻

22. Security Alerts

Command:

/security_alerts

⸻

Response:

Duplicate Wallet
Duplicate CCCD
Multiple Failed Login Attempts
Suspicious Activity

⸻

23. Create Admin

Super Admin Only.

Command:

/create_admin <user_id>

⸻

Requirements:

Super Admin
2FA Verified

⸻

24. Disable Admin

Command:

/disable_admin <user_id>

⸻

Requirements:

Super Admin
2FA Verified

⸻

25. Audit Logs

Command:

/audit_logs

⸻

Returns:

Recent Admin Actions
Security Events
Critical Operations

⸻

26. Group Chat Rules

Allowed:

/help

⸻

Blocked:

/register
/login
/kyc
/ekyc
/profile
/add_wallet

⸻

Response:

Please continue in private chat.

⸻

27. Notification Events

Bot automatically notifies:

Registration Completed
Password Changed
2FA Enabled
KYC Approved
KYC Rejected
eKYC Approved
Wallet Verified
Credits Added

⸻

28. Acceptance Criteria

Commands complete when:

✓ Register works

✓ Login works

✓ 2FA works

✓ Profile works

✓ KYC works

✓ eKYC works

✓ Wallet works

✓ Credits work

✓ Admin commands work

✓ Super Admin commands work

✓ Group restrictions work

✓ Notifications work

✓ API integration matches backend design