P2PSuperBot — Phase 1 Scope

1. Objective

Phase 1 focuses on building the foundation of P2PSuperBot.

The goal is to complete the core identity, security, profile, KYC/eKYC, wallet, and credit foundation before implementing trading-related features.

Phase 1 must make sure that users can:

* Register with email
* Activate account security
* Login securely
* Enable Google Authenticator 2FA
* Upload KYC/eKYC documents
* Build a verified profile
* Add and verify crypto wallets
* Receive and consume internal Credits
* Be reviewed by admin

Phase 1 is the foundation for later P2P trading, escrow, dispute, trust score, and community verification features.

⸻

2. Phase 1 Modules

Phase 1 includes the following modules:

1. Register
2. Login
3. Password Management
4. Google Authenticator 2FA
5. Profile
6. KYC / eKYC
7. Wallet Verification
8. Credits Basic Ledger
9. Admin Review Basic
10. Bot Routing and Security Rules

⸻

3. Phase 1 User Flow

B1 — Email Registration

User starts registration in private chat.

User only provides:

* Email address

System creates:

* Internal User ID
* Temporary password
* 2FA activation token
* Registration status

System sends email containing:

* User ID
* Temporary password
* 2FA activation token
* First login instructions
* Password change instructions
* Google Authenticator activation instructions
* Third-party eKYC instruction
* Instruction to export eKYC result as PDF
* Instruction to upload eKYC PDF to the bot after security activation

Status after B1:

* B1_EMAIL_SENT
* WAITING_FIRST_LOGIN

⸻

B2 — Security Activation

User logs in using:

* User ID or email
* Temporary password

After successful first login, system requires:

1. Change temporary password
2. Activate Google Authenticator 2FA
3. Login again using new password + 2FA code

Rules:

* Temporary password must be single-use.
* Temporary password must expire.
* 2FA activation token must be single-use.
* Password must never be displayed back to the user.
* Password must never be stored in plaintext.
* 2FA secret must be stored securely.

Status after B2:

* B2_SECURITY_COMPLETED

⸻

B3 — KYC / eKYC Verification

After B2 is completed, user can submit identity verification.

There are two verification paths:

Path A — eKYC PDF

User performs eKYC through a third-party provider.

User uploads:

* eKYC result PDF

System:

* Stores PDF securely
* Parses PDF text
* Extracts identity data
* Creates/updates profile from extracted data
* Sends data to admin review

eKYC has higher trust value than manual KYC.

Path B — Manual KYC

If user does not complete third-party eKYC, user may upload:

* CCCD/ID front image
* CCCD/ID back image
* Selfie image

System:

* Stores images securely
* Uses OCR where possible
* Extracts identity data
* Sends data to admin review

Manual KYC is not eKYC. It has lower trust value than eKYC.

Status after B3:

* KYC_PENDING_REVIEW
* KYC_APPROVED
* KYC_REJECTED
* EKYC_PENDING_REVIEW
* EKYC_APPROVED
* EKYC_REJECTED

⸻

B4 — Wallet Verification and Credits

After B3 is approved, user can add and verify crypto wallets.

Supported wallet types in Phase 1:

* TRON wallet
* BNB/BSC wallet

Wallet categories:

* Primary wallet
* Secondary wallet
* Exchange wallet
* Cold wallet

Wallet verification method:

* User adds wallet address.
* System creates wallet verification request.
* User transfers the required minimum amount from that wallet to the system verification wallet.
* System checks blockchain transaction.
* If valid, wallet is verified.
* Credits are added to user account.

Example:

* Minimum TRON verification deposit: 50 TRX
* Credit conversion: 1 TRX = 10 Credits
* 50 TRX = 500 Credits

Credits are internal utility credits only.

Credits can be used for:

* Check wallet
* Check user
* Check bank later
* Advanced report later
* OCR/manual verification cost
* Other P2PSuperBot services

Credits cannot be:

* Transferred between users
* Traded
* Withdrawn
* Converted back to crypto or fiat
* Used as payment for P2P asset trades

⸻

4. Admin Review Scope

Phase 1 includes only basic admin review.

Admin can:

* Search user
* View masked user information
* View verification status
* Review KYC submission
* Review eKYC PDF result
* Approve KYC/eKYC
* Reject KYC/eKYC with reason
* Review wallet verification status
* View basic credit ledger

Sensitive information must be masked by default.

Examples:

* Email: hu***@gmail.com
* Phone: 097****677
* Telegram ID: 123****789
* CCCD: 079*****789
* Wallet: TAbc****9XYZ

Full reveal is not part of Phase 1 unless required for admin review. If implemented, full reveal must require:

* Admin permission
* Reason
* Google Authenticator verification
* Audit log

⸻

5. Bot Interaction Rules

All sensitive flows must happen only in private chat.

Private chat only:

* Register
* Login
* Password change
* 2FA setup
* KYC/eKYC upload
* Wallet add
* Wallet verification
* Credit balance

Group chat:

* Must not collect email, password, OTP, 2FA code, KYC, wallet verification data, or any sensitive information.
* If /register or /login is used in group, bot must reply with private chat deep link only.
* Group must act only as public gateway, not as sensitive data collection channel.

Example group response:

🔐 For security reasons, please continue in private chat with the bot.

Deep link:

https://t.me/<BOT_USERNAME>?start=register
https://t.me/<BOT_USERNAME>?start=login

⸻

6. Security Rules

Password

Password must never be:

* Stored in plaintext
* Logged
* Displayed back to user
* Masked and shown
* Sent again after setup
* Visible to admin

Store only:

* Password hash
* Password changed timestamp
* Failed login count
* Password reset state if needed

OTP / 2FA

Never log:

* OTP
* TOTP code
* Google Authenticator secret
* Recovery code

2FA must be required for:

* Login after B2
* Sensitive actions
* Wallet verification confirmation
* Future trading actions

Sensitive data masking

Mask by default:

* Email
* Phone
* CCCD/passport number
* Bank account
* Wallet address
* Telegram ID

⸻

7. Credits Rules

Credits are internal service credits.

Credits can be created from:

* TRX deposit
* BNB deposit
* Wallet verification deposit
* Future charity contribution record
* Promotions or admin adjustment

In Phase 1, priority is:

* TRX/BNB based Credits
* Wallet verification deposit Credits

Credits must be tracked with a ledger.

Ledger must record:

* User ID
* Credit amount
* Transaction type
* Balance before
* Balance after
* Reference ID
* Created at

Credit transaction examples:

* WALLET_VERIFICATION_REWARD
* CREDIT_TOPUP_TRX
* CREDIT_TOPUP_BNB
* CHECK_WALLET_FEE
* ADMIN_ADJUSTMENT

⸻

8. Out of Scope for Phase 1

The following features are not included in Phase 1:

* P2P buy/sell order posting
* Group marketplace posts
* Escrow
* Dispute handling
* Bank verification
* Charity fund dashboard
* Monthly charity report
* Merchant program
* Affiliate program
* Advanced Trust Score
* Advanced Risk Engine
* TXID reputation network
* Relationship graph
* Exchange account verification
* Full admin RBAC system
* Public check groups
* Advanced monitoring dashboard

These features will be implemented in later phases after Phase 1 is stable.

⸻

9. Phase 1 Success Criteria

Phase 1 is complete when:

* Bot responds correctly to /start, /register, /login, /help, /cancel in private chat.
* Bot does not collect sensitive data in groups.
* User can register with email.
* System sends User ID, temporary password, 2FA activation token, and instructions by email.
* User can login first time.
* User must change temporary password.
* User can activate Google Authenticator.
* User must login again using new password and 2FA.
* User can upload eKYC PDF.
* System can store and parse eKYC PDF.
* User can upload manual KYC images if eKYC PDF is not available.
* Admin can review and approve/reject KYC/eKYC.
* User can add TRON/BNB wallet.
* User can verify wallet using blockchain deposit.
* System can add Credits after valid wallet verification deposit.
* Credits ledger records all credit changes.
* Sensitive data is masked by default.
* Password, OTP, 2FA secret, and tokens are never logged or displayed.
* All important actions are audit logged.

⸻

10. Technical Foundation

Recommended stack for Phase 1:

* Python
* aiogram or equivalent Telegram bot framework
* FastAPI backend if separated
* PostgreSQL
* Redis
* Worker queue for heavy jobs
* SMTP email provider
* PDF parser
* OCR module for manual KYC
* Blockchain API for TRON and BNB/BSC verification

Bot must not process heavy tasks directly.

Heavy tasks should be sent to backend/worker:

* Email sending
* PDF parsing
* OCR
* Blockchain transaction check
* Wallet verification
* Credit ledger update

Bot should:

* Receive input
* Validate basic format
* Create request/job
* Reply quickly with request status
* Notify user when backend processing is completed