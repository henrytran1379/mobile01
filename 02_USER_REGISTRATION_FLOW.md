P2PSuperBot — User Registration Flow

1. Objective

The registration module is responsible for:

* Creating a new user account.
* Validating email ownership.
* Generating initial credentials.
* Creating the first security session.
* Preparing the user for account activation.

Registration must be simple.

User should only provide:

* Email address

No other information is collected during registration.

⸻

2. Registration Entry Points

Allowed:

/register
/start register

Private chat only.

If registration is initiated in a group:

Bot must respond:

“Please continue registration in private chat.”

No registration data may be collected in groups.

⸻

3. Registration Flow

Step 1

User:

/register

Bot:

Please enter your email address.

⸻

Step 2

User submits email.

Example:

user@gmail.com

⸻

Step 3

System validates:

* Email format
* Email length
* Disposable email policy (optional)
* Existing email check

Possible responses:

Invalid email format.

or

Email already registered.

⸻

Step 4

System creates account.

Generate:

User ID
Temporary Password
2FA Activation Token
Registration Session ID

Example:

User ID:
U20260611-000001
Temporary Password:
Random secure password
2FA Token:
Random activation token

⸻

Step 5

Store user.

Initial status:

ACCOUNT_CREATED
WAITING_FIRST_LOGIN

⸻

Step 6

Send registration email.

Email contains:

* User ID
* Temporary Password
* 2FA Activation Token
* First login instructions
* Password change instructions
* Google Authenticator setup instructions
* eKYC instructions
* eKYC PDF upload instructions

⸻

Step 7

Bot response.

Registration successful.
Please check your email.
Your account activation instructions have been sent.

⸻

4. User States

ACCOUNT_CREATED

Account exists.

No login yet.

⸻

WAITING_FIRST_LOGIN

Email sent.

Waiting for first login.

⸻

ACTIVATION_EXPIRED

Temporary credentials expired.

Requires regeneration.

⸻

ACCOUNT_ACTIVATED

B2 completed.

⸻

5. Expiration Rules

Temporary password:

30 minutes

2FA activation token:

30 minutes

Registration session:

24 hours

Expired credentials must be regenerated.

⸻

6. Resend Registration

Command:

/resend_activation

Requirements:

* Existing email
* Account not activated

System generates:

* New temporary password
* New 2FA token

Old credentials become invalid.

⸻

7. Duplicate Protection

A Telegram account cannot create unlimited registrations.

Recommended limits:

5 registrations/day

Email uniqueness:

UNIQUE(email)

User ID uniqueness:

UNIQUE(user_id)

⸻

8. Audit Log

Log:

registration_created
registration_email_sent
registration_resent
registration_expired

Do not log:

password
2fa token
otp

⸻

9. Database Objects

Tables involved:

users
user_security
registration_sessions
audit_logs

⸻

10. Acceptance Criteria

Registration is complete when:

* User enters valid email.
* User account is created.
* User ID generated.
* Temporary password generated.
* 2FA activation token generated.
* Registration email sent.
* Account state updated.
* Audit log created.
* Sensitive credentials never logged.

:::
Sau file này, thứ tự tiếp theo nên là:
```text
03_LOGIN_SECURITY_2FA_FLOW.md
04_PROFILE_KYC_EKYC_FLOW.md
05_WALLET_CREDIT_FLOW.md
06_DATABASE_DESIGN_PHASE1.md

Đây là 4 tài liệu quan trọng nhất trước khi viết prompt Codex triển khai Phase 1.