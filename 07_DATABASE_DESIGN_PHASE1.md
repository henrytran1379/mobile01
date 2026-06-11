P2PSuperBot — Database Design Phase 1

1. Objective

This document defines the PostgreSQL schema for Phase 1.

Phase 1 covers:

* Register
* Login
* Security
* 2FA
* Profile
* KYC
* eKYC
* Wallet
* Credits
* Admin Review
* Audit Logging

Database must be designed for future expansion.

⸻

2. Naming Convention

Tables:

snake_case
plural

Example:

users
user_profiles
user_wallets

⸻

Primary Keys:

id UUID

⸻

Timestamps:

created_at
updated_at

UTC only.

⸻

3. Core User Tables

users

Stores account identity.

id UUID PK
user_code VARCHAR(50) UNIQUE
telegram_id BIGINT UNIQUE
telegram_username VARCHAR(100)
email VARCHAR(255) UNIQUE
status VARCHAR(50)
role VARCHAR(50)
created_at
updated_at

⸻

Status:

ACCOUNT_CREATED
WAITING_FIRST_LOGIN
ACTIVE
LOCKED
SUSPENDED
DISABLED

⸻

Role:

USER
ADMIN
SUPER_ADMIN

⸻

4. User Security

user_security

Stores authentication settings.

id UUID PK
user_id UUID FK
password_hash TEXT
password_changed_at TIMESTAMP
two_factor_enabled BOOLEAN
two_factor_secret TEXT
failed_login_count INTEGER
locked_until TIMESTAMP
last_login_at TIMESTAMP
created_at
updated_at

⸻

5. Registration Sessions

registration_sessions

id UUID PK
user_id UUID FK
temporary_password_hash TEXT
activation_token_hash TEXT
expires_at TIMESTAMP
used BOOLEAN
created_at

⸻

6. User Sessions

user_sessions

id UUID PK
user_id UUID FK
session_token_hash TEXT
refresh_token_hash TEXT
ip_address VARCHAR(100)
device_info TEXT
expires_at TIMESTAMP
is_active BOOLEAN
created_at

⸻

7. Recovery Codes

recovery_codes

id UUID PK
user_id UUID FK
code_hash TEXT
used BOOLEAN
used_at TIMESTAMP
created_at

⸻

8. User Profile

user_profiles

id UUID PK
user_id UUID FK
full_name VARCHAR(255)
date_of_birth DATE
gender VARCHAR(20)
nationality VARCHAR(100)
avatar_url TEXT
created_at
updated_at

⸻

9. Government Identity

user_identity_documents

id UUID PK
user_id UUID FK
identity_number VARCHAR(50)
issue_date DATE
issue_place VARCHAR(255)
expiry_date DATE
document_type VARCHAR(50)
created_at
updated_at

⸻

10. KYC Submissions

kyc_submissions

id UUID PK
user_id UUID FK
front_image_url TEXT
back_image_url TEXT
selfie_image_url TEXT
ocr_data JSONB
status VARCHAR(50)
submitted_at TIMESTAMP
reviewed_at TIMESTAMP

⸻

Status:

PENDING
APPROVED
REJECTED

⸻

11. eKYC Submissions

ekyc_submissions

id UUID PK
user_id UUID FK
provider_name VARCHAR(100)
provider_reference VARCHAR(255)
pdf_url TEXT
parsed_data JSONB
status VARCHAR(50)
submitted_at TIMESTAMP
reviewed_at TIMESTAMP

⸻

12. Verification Reviews

verification_reviews

id UUID PK
user_id UUID FK
review_type VARCHAR(50)
review_status VARCHAR(50)
admin_id UUID
reason TEXT
created_at

⸻

Review Types:

KYC
EKYC
WALLET

⸻

13. User Wallets

user_wallets

id UUID PK
user_id UUID FK
network VARCHAR(50)
wallet_address VARCHAR(255)
wallet_type VARCHAR(50)
status VARCHAR(50)
verified_at TIMESTAMP
created_at
updated_at

⸻

Wallet Types:

PRIMARY
SECONDARY
EXCHANGE
COLD

⸻

14. Wallet Verifications

wallet_verifications

id UUID PK
wallet_id UUID FK
verification_address VARCHAR(255)
txid VARCHAR(255)
amount NUMERIC(38,18)
status VARCHAR(50)
verified_at TIMESTAMP
created_at

⸻

15. Credit Accounts

credit_accounts

One account per user.

id UUID PK
user_id UUID UNIQUE
balance BIGINT
total_earned BIGINT
total_spent BIGINT
created_at
updated_at

⸻

16. Credit Ledger

credit_ledger

id UUID PK
user_id UUID FK
ledger_type VARCHAR(100)
amount BIGINT
balance_before BIGINT
balance_after BIGINT
reference_id UUID
description TEXT
created_at

⸻

Ledger Types:

TRX_TOPUP
BNB_TOPUP
WALLET_VERIFICATION
CHECK_WALLET
CHECK_USER
ADMIN_ADJUSTMENT

⸻

17. Admin Users

admin_users

id UUID PK
user_id UUID UNIQUE
admin_level VARCHAR(50)
is_active BOOLEAN
created_at

⸻

18. Admin Roles

admin_roles

id UUID PK
role_name VARCHAR(100)
description TEXT
created_at

⸻

19. Review Queue

review_queue

id UUID PK
review_type VARCHAR(50)
target_id UUID
priority INTEGER
status VARCHAR(50)
assigned_admin UUID
created_at
updated_at

⸻

20. Security Alerts

security_alerts

id UUID PK
user_id UUID
alert_type VARCHAR(100)
severity VARCHAR(50)
status VARCHAR(50)
details JSONB
created_at

⸻

21. Audit Logs

audit_logs

Most important table.

id UUID PK
actor_id UUID
actor_type VARCHAR(50)
action VARCHAR(100)
target_id UUID
target_type VARCHAR(100)
reason TEXT
metadata JSONB
ip_address VARCHAR(100)
created_at

⸻

Actor Types:

USER
ADMIN
SYSTEM

⸻

22. File Storage

user_documents

id UUID PK
user_id UUID
document_type VARCHAR(50)
file_url TEXT
file_hash TEXT
is_encrypted BOOLEAN
created_at

⸻

Document Types:

CCCD_FRONT
CCCD_BACK
SELFIE
EKYC_PDF

⸻

23. Future Reserved Tables

Not Phase 1.

Reserved:

banks
bank_verifications
txid_records
user_relationships
trust_scores
reputation_scores
risk_scores
p2p_orders
escrow_orders
disputes
affiliate_accounts
charity_contributions

⸻

24. Index Strategy

Required:

users(email)
users(telegram_id)
users(user_code)
user_wallets(wallet_address)
user_identity_documents(identity_number)
credit_ledger(user_id)
audit_logs(actor_id)
audit_logs(target_id)

⸻

25. Data Retention

Audit Logs:

Permanent

⸻

KYC/eKYC:

Permanent

⸻

Sessions:

90 Days

⸻

Security Alerts:

5 Years

⸻

26. Acceptance Criteria

Database design complete when:

✓ Supports Register

✓ Supports Login

✓ Supports 2FA

✓ Supports KYC

✓ Supports eKYC

✓ Supports Wallet Verification

✓ Supports Credits

✓ Supports Admin Review

✓ Supports Audit Logging

✓ Supports Future Expansion

✓ No schema redesign required for Phase 2