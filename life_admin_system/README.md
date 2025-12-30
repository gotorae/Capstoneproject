# Capstoneproject
Simple Life Insurance administration system


# Life Admin System

A secure, modular Django-based administration system for managing life insurance policies, receipts, billing, claims, cancellations, commissions, and user access control.

This system is designed for **enterprise-grade insurance administration**, with strong emphasis on **security, auditability, and correctness**.

---

## 🧩 Core Features

- Policy lifecycle management
- Premium receipt processing with auto-generated receipt numbers
- Upload & batch import approval workflow
- Policy cancellation requests & approvals
- Claims registration and tracking
- Agent & commission management
- Secure admin and REST API access
- Full audit logging
- Extensive automated test coverage

---

## 🏗️ Project Structure

```text
life_admin_system/
│
├── life_admin_system/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│
├── access/            # Custom user model (Administrator)
├── agents/
├── billing/
├── cancellations/
├── claims/
├── clients/
├── commissions/
├── paypoints/
├── policies/
├── receipts/
│   ├── services.py    # Upload processing logic
│   ├── resources.py   # Import-export resources
│
├── manage.py
└── README.md


🔐 Security Design

The system follows Django security best practices.

Implemented Protections

CSRF protection enabled globally

Secure cookies (HTTPS only)

Clickjacking protection

XSS & MIME sniffing protection

HTTP Strict Transport Security (HSTS)

Content Security Policy (CSP)

Role-based admin permissions

Token + Session authentication

Audit logging via django-auditlog

Key Settings (Production)
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

👤 User & Access Control

Custom user model: Administrator

Supports:

Staff users

Superusers

Admin actions restricted by role

Sensitive actions (approvals, imports) limited to superusers

📄 Policies

Policies represent active insurance contracts.

Key Fields

Client

Agent

Paypoint

Product code & name

Duration & frequency

Total premium due

Automatically tracked total received

Business Rules

Premium receipts update policy totals automatically

Only active policies can be cancelled

Policies cannot be cancelled twice

💵 Premium Receipts

Receipt numbers auto-generated:

Rec00001
Rec00002


Each receipt:

Is linked to a policy

Updates policy total received

Stores the user who receipted it

📥 Upload & Batch Processing
Workflow

File uploaded

Awaiting approval

Superuser approves upload

Data processed via services.py

Errors reported per upload

Safety

Uploads cannot be processed twice

Rejection prevents processing

All actions audited

❌ Policy Cancellations
Lifecycle

Request created → REQUESTED

Admin approves → APPROVED

Status locked after approval

Validation Rules

Only active policies can be cancelled

Effective date cannot be in the past

Duplicate cancellations are blocked

🌐 REST API

Built using Django REST Framework

Authentication

Session Authentication

Token Authentication

Permissions

Read-only access for unauthenticated users

Full access for authenticated users

Example Endpoints
Method	Endpoint	Description
GET	/api/policies/	List policies
POST	/api/receipts/	Create receipt
POST	/api/cancellations/	Request cancellation
POST	/api/cancellations/{id}/approve/	Approve cancellation
🧪 Automated Testing

The system includes full test coverage.

Test Categories

Model validation

Business logic

Admin permissions

API authentication

Upload approval workflows

Aggregation logic

Security regression tests

Run Tests
python manage.py test

📦 Installation
1️⃣ Clone Repository
git clone <repository-url>
cd life_admin_system

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Apply Migrations
python manage.py migrate

5️⃣ Create Superuser
python manage.py createsuperuser

6️⃣ Run Server
python manage.py runserver

📊 Admin Interface

Access admin at:

/admin/

Admin Capabilities

Policy management

Receipt entry

Upload approvals

Cancellation approvals

Claims management

Audit log review

📚 Technology Stack

Python 3.12+

Django 5.2

Django REST Framework

SQLite (dev) / PostgreSQL (prod)

django-import-export

django-auditlog

django-filter

🧭 Future Enhancements

PDF policy schedules

Payment gateway integration

Email notifications

Role-based API permissions

Async background processing (Celery)

Coverage reports

🧑‍💻 Author

Effort Gotora
Capstone Project – Insurance Administration System

✅ Status

✔ Secure
✔ Tested
✔ Production-ready architecture
✔ Extensible


---

## 🎯 NEXT OPTIONS

When ready, we can add:

- **API documentation (Swagger / OpenAPI)**
- **Deployment guide (Nginx + Gunicorn)**
- **Database migration strategy**
- **CI/CD pipeline**
- **Security audit report**

Just say the word 👌
