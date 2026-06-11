P2PSuperBot — Login, Security & 2FA Flow

1. Objective

This module is responsible for:

* Secure account login
* First-time account activation
* Password management
* Google Authenticator 2FA
* Password recovery
* Session management
* Security auditing

The goal is to ensure every verified user account has strong authentication before accessing Profile, KYC/eKYC, Wallet, Credits, and future P2P functions.

⸻

2. Security Principles

The following rules are mandatory:

Never Store Plaintext Passwords

Passwords must:

* Never be stored in plaintext
* Never be logged
* Never be displayed back to users
* Never be visible to admins

Store only:

* Password hash
* Password created timestamp
* Password changed timestamp

Recommended:

bcrypt
argon2

⸻

Never Store OTP Codes

Never store:

OTP
TOTP
Google Authenticator Codes

Store only:

2FA Secret
Encrypted Secret

⸻

Sensitive Data Logging

The following must never appear in logs:

Password
OTP
TOTP
2FA Secret
Recovery Codes
JWT Tokens
Session Tokens

⸻

3. Login Methods

Phase 1 supports:

Login by Email

Example:

Email:
user@gmail.com
Password:
********

⸻

Login by User ID

Example:

User ID:
USR-20260611-000001
Password:
********

⸻

4. First Login Flow

After registration (B1), user receives:

User ID
Temporary Password
2FA Activation Token

Status:

WAITING_FIRST_LOGIN

⸻

Step 1

User enters:

/login

Bot asks:

User ID or Email

User submits.

Bot asks:

Password

User submits temporary password.

⸻

Step 2

System validates:

Account Exists
Temporary Password Valid
Temporary Password Not Expired
Account Active

⸻

Step 3

System forces password change.

User cannot continue until password is changed.

Status:

PASSWORD_CHANGE_REQUIRED

⸻

Step 4

User creates new password.

Password policy:

Minimum:

12 characters
1 uppercase
1 lowercase
1 number
1 special character

Example:

P2PSuper@2026

⸻

Step 5

Password stored as hash.

Temporary password immediately invalidated.

⸻

Step 6

System forces Google Authenticator activation.

Status:

2FA_SETUP_REQUIRED

⸻

5. Google Authenticator Setup

Supported:

Google Authenticator
Microsoft Authenticator
Authy

Protocol:

RFC6238 TOTP

⸻

Step 1

Generate:

2FA Secret

Generate:

QR Code

Display QR Code.

⸻

Step 2

User scans QR.

⸻

Step 3

User enters first 6-digit code.

Example:

123456

⸻

Step 4

System verifies.

If valid:

2FA Enabled

Status:

2FA_ACTIVE

⸻

Step 5

Generate Recovery Codes.

Example:

ABCD-1234
EFGH-5678
IJKL-9012
...

Store hashed versions only.

User instructed to save them securely.

⸻

6. Security Activation Complete

When:

Password Changed
AND
2FA Activated

Status:

B2_SECURITY_COMPLETED

User must logout.

⸻

7. Second Login

User logs in again.

Required:

Email/User ID
Password
2FA Code

Successful login creates:

Authenticated Session

⸻

8. Session Management

Each login creates:

Session ID
Access Token
Refresh Token

Track:

IP Address
Telegram User ID
Device Info
Login Time

⸻

Session Expiration

Access Token:

15 minutes

Refresh Token:

7 days

Configurable.

⸻

9. Failed Login Protection

Track:

Failed Login Count

Rules:

5 failed attempts

Result:

Account Locked
15 minutes

Status:

ACCOUNT_LOCKED

⸻

Repeated Abuse

Optional:

30 minutes
1 hour
24 hours

Escalation.

⸻

10. Password Change

Command:

/change_password

Requirements:

Current Password
New Password
2FA Code

⸻

Validation

New password:

Cannot equal current password
Cannot equal temporary password
Must pass policy

⸻

11. Password Reset

Command:

/reset_password

⸻

Step 1

User provides:

Email

⸻

Step 2

System sends:

Password Reset Link
Reset Token

⸻

Step 3

User creates new password.

⸻

Step 4

User must login again using:

New Password
2FA

⸻

12. Recovery Codes

Used when:

Phone Lost
Authenticator Lost

Each recovery code:

Single Use

After use:

Immediately Invalidated

⸻

13. Account Status Model

Possible statuses:

ACCOUNT_CREATED
WAITING_FIRST_LOGIN
PASSWORD_CHANGE_REQUIRED
2FA_SETUP_REQUIRED
2FA_ACTIVE
B2_SECURITY_COMPLETED
ACCOUNT_LOCKED
PASSWORD_RESET_PENDING
ACCOUNT_DISABLED

⸻

14. Audit Log Events

Log:

LOGIN_SUCCESS
LOGIN_FAILED
ACCOUNT_LOCKED
PASSWORD_CHANGED
PASSWORD_RESET_REQUESTED
PASSWORD_RESET_COMPLETED
2FA_ENABLED
2FA_DISABLED
RECOVERY_CODE_USED
LOGOUT

⸻

15. Telegram Rules

All login and security actions:

Private Chat Only

Never allow:

Password
2FA
OTP
Recovery Codes

inside group chats.

⸻

16. Database Tables

Phase 1 tables:

users
user_security
user_sessions
password_history
recovery_codes
audit_logs

⸻

17. Acceptance Criteria

This module is complete when:

✓ User can login using temporary password

✓ User is forced to change password

✓ User is forced to activate Google Authenticator

✓ Recovery codes generated

✓ User can login using password + 2FA

✓ Failed login lockout works

✓ Password reset works

✓ Session management works

✓ Audit logs generated

✓ No passwords stored in plaintext

✓ No OTP/TOTP values logged

✓ All security operations restricted to private chat

✓ User status correctly progresses to:

B2_SECURITY_COMPLETED