CODEX_IMPLEMENT_SPRINT_1_DATABASE

Role:

You are the Primary Implementation Agent for P2PSuperBot.

Your task is to implement Sprint 1 exactly as specified.

Do not implement future sprints.

Do not redesign approved specifications.

⸻

PRE-READ REQUIREMENTS

Read in order:

1. PROJECT_STATUS_DASHBOARD.md
2. PROJECT_MEMORY.md
3. 10_PHASE1_MASTER_SPECIFICATION.md
4. 11_PHASE1_IMPLEMENTATION_ROADMAP.md
5. 07_DATABASE_DESIGN_PHASE1.md
6. 14_CODEX_STARTUP_PROMPT.md

Do not begin implementation until all files have been reviewed.

⸻

SPRINT INFORMATION

Sprint:

Sprint 1
Database Foundation

Status:

IN PROGRESS

Goal:

Build the complete database foundation for Phase 1.

⸻

OBJECTIVES

Implement:

✓ SQLAlchemy Models

✓ Alembic Migrations

✓ Repository Layer

✓ Base CRUD Operations

✓ Database Configuration

✓ Database Unit Tests

✓ Database Integration Tests

⸻

DATABASE TABLES

Create SQLAlchemy models for:

users
user_security
registration_sessions
user_sessions
recovery_codes
user_profiles
user_identity_documents
kyc_submissions
ekyc_submissions
verification_reviews
user_wallets
wallet_verifications
credit_accounts
credit_ledger
admin_users
admin_roles
review_queue
security_alerts
audit_logs
user_documents

⸻

MODEL REQUIREMENTS

All models must:

Use:

UUID Primary Keys

Include:

created_at
updated_at

Use:

SQLAlchemy 2.0 style

Use:

Declarative Base

Support:

PostgreSQL

⸻

DATABASE CONFIGURATION

Implement:

backend/core/database.py

Responsibilities:

* Engine Creation
* Session Factory
* Dependency Injection
* Connection Health Check

Requirements:

Async SQLAlchemy

⸻

BASE MODEL

Create:

backend/models/base.py

Responsibilities:

* UUID PK
* created_at
* updated_at

Reusable by all models.

⸻

REPOSITORY LAYER

Create:

backend/repositories/

Implement:

BaseRepository

Functions:

create()
get_by_id()
update()
delete()
list()
exists()

⸻

Create specialized repositories:

UserRepository
UserSecurityRepository
ProfileRepository
WalletRepository
CreditRepository

⸻

ALEMBIC

Configure:

alembic/

Requirements:

* Initial Migration
* Schema Versioning
* Upgrade Support
* Downgrade Support

Generate:

Initial Database Migration

⸻

INDEXES

Implement all indexes defined in:

07_DATABASE_DESIGN_PHASE1.md

Including:

users(email)
users(user_code)
users(telegram_id)
user_wallets(wallet_address)
credit_ledger(user_id)
audit_logs(actor_id)
audit_logs(target_id)

⸻

CONSTRAINTS

Implement:

Unique Constraints

Foreign Keys

Check Constraints

Required Indexes

Cascade Rules

⸻

TESTING REQUIREMENTS

Create:

tests/unit/database/

Tests:

Model Creation
Repository CRUD
Validation
Relationships

⸻

Create:

tests/integration/database/

Tests:

Migration Execution
Database Connection
CRUD Integration
Foreign Keys
Unique Constraints

⸻

ACCEPTANCE CRITERIA

Database schema created successfully.

All migrations execute successfully.

All repositories functional.

All constraints enforced.

All indexes created.

All unit tests pass.

All integration tests pass.

No failing tests allowed.

⸻

VALIDATION COMMANDS

Run:

pytest tests/unit/database -v

Run:

pytest tests/integration/database -v

Run:

pytest -v

Fix all failures.

Do not ignore failing tests.

⸻

DELIVERABLES

Create:

backend/models/
backend/repositories/
backend/core/database.py
alembic/
tests/unit/database/
tests/integration/database/

⸻

DOCUMENTATION UPDATE

Update:

PROJECT_STATUS_DASHBOARD.md

Change:

Sprint 1
IN PROGRESS
↓
COMPLETED

Update progress percentage.

⸻

COMPLETION REPORT

Create:

SPRINT_1_COMPLETION_REPORT.md

Include:

1. Summary
2. Files Created
3. Files Modified
4. Migrations Created
5. Tests Added
6. Test Results
7. Known Issues
8. Next Sprint Recommendation

⸻

GIT COMMIT

After all tests pass:

Create commit:

[Sprint-1]
Database Foundation Completed

Push to repository.

⸻

DEFINITION OF DONE

Sprint 1 is complete only when:

✓ Models Created

✓ Repositories Created

✓ Alembic Configured

✓ Migration Successful

✓ Unit Tests Pass

✓ Integration Tests Pass

✓ Dashboard Updated

✓ Completion Report Created

✓ Git Commit Created

Only then may Sprint 1 be marked COMPLETE.

END OF DOCUMENT