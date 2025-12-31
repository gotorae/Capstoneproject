# **Life Admin System**
_A Django-based Funeral Affinity & Micro Insurance Management Platform_

> Built to demonstrate a complete, secure, and auditable life insurance back‑office for funeral & affinity products. Includes policy administration, receipts, claims, cancellations, billing, agent commissions, and paypoint management—exposed via Django Admin and REST APIs.

---

## 📌 Table of Contents
- #overview
- #key-features
- #architecture
- #tech-stack
- #setup--installation
- #configuration
- #usage
- #data-model-highlights
- #api-documentation
- #security--compliance
- #admin-workflows
- #pre-deployment-checklist
- #future-enhancements
- #license

---

## 🧭 Overview
**Life Admin System** is a secure Django application tailored for **funeral affinity / micro insurance** operations. It supports:
- Policy lifecycle (create → status calculation → financials)
- Premium receipting (auto number generation + running totals)
- Claims intake and approval (with supporting documents)
- Cancellations workflow
- Monthly **billing** per paypoint
- **Commission** statements per agent (CSV/PDF/Email)
- **Audit logging** on key actions
- Hardened settings for production (CSP, HSTS, SSL redirects)

Designed to be shared internally and extended for enterprise deployment.

---

## 🚀 Key Features
- **Custom Auth**: `access.Administrator` as the `AUTH_USER_MODEL`.
- **Policies**:
  - Product types: **Funeral**, **Affinity** with `product_code` auto-set.
  - Monthly premium derived from **cover** and **frequency**.
  - Dynamic properties: `months_paid`, `months_in_arrears`, `policy_status`, and **overall status** (combines claim/cancellation + lifecycle).
- **Receipts**:
  - Auto receipt numbers (`Rec000001`, …).
  - Atomic updates to `policy.total_premium_received`.
- **Claims**:
  - Document uploads: claim form + burial order/death certificate.
  - Approval path with optional email to Finance.
- **Cancellations**:
  - Requested → Approved with validations and effective date handling.
- **Billing**:
  - Per paypoint, per month; export to **CSV/PDF**.
- **Commissions**:
  - Per agent, per month; monthly rate derived from policy frequency.
  - Export **CSV/PDF** or **Email** the statement to the agent.
- **Audit & Export**:
  - `django-auditlog` everywhere it matters.
  - `django-import-export` on admin resources.
- **Security**:
  - `django-csp` + strict security headers in settings.

---

## 🧱 Architecture
```
life_admin_system/
├── access/           # Custom user model (Administrator)
├── agents/           # Agents + file uploads
├── clients/          # Clients + file uploads
├── paypoints/        # Paypoint registry
├── policies/         # Policies: lifecycle, financials, status
├── receipts/         # Premium receipting + uploads
├── claims/           # Claims intake & approval
├── cancellations/    # Cancellation workflow
├── billing/          # Monthly billing statements
├── commissions/      # Agent commission statements
├── templates/        # Optional server-side templates
└── life_admin_system/
    ├── settings.py   # Hardened settings & DRF config
    ├── urls.py       # API & admin routes
    └── wsgi.py
```

---

## 🛠️ Tech Stack
- **Backend**: Django 4+, Django REST Framework
- **Auth**: Session + Token (`rest_framework.authtoken`)
- **Filters/Search**: `django-filter`, DRF search/order
- **Security**: `django-csp`, secure headers, HSTS/SSL in prod
- **Audit**: `django-auditlog`
- **Admin import/export**: `django-import-export`
- **PDF**: `reportlab`
- **File uploads**: Django `FileField` / `ImageField`

---

## ⚙️ Setup & Installation

```bash
# 1) Clone
git clone https://your.git.server/life_admin_system.git
cd life_admin_system

# 2) Virtual env
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3) Install deps
pip install -r requirements.txt

# 4) Migrate
python manage.py migrate

# 5) Create admin user
python manage.py createsuperuser

# 6) Run dev server
python manage.py runserver
```

### `requirements.txt` (sample)
```txt
Django>=4.2,<5.1
djangorestframework>=3.15
django-filter>=24.2
django-auditlog>=2.3.0
django-import-export>=3.3.1
django-csp>=3.8
reportlab>=4.2
Pillow>=10.2
python-dotenv>=1.0
# Database drivers (choose one in production)
psycopg2-binary>=2.9   # PostgreSQL
mysqlclient>=2.2       # MySQL/MariaDB
```

---

## 🔧 Configuration
Create `.env` (or set environment variables):

```env
DJANGO_ENV=development    # or production
DJANGO_SECRET_KEY=change-me
DEFAULT_FROM_EMAIL=noreply@yourcompany.co.zw
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

Key `settings.py` highlights:
- `AUTH_USER_MODEL = "access.Administrator"`
- DRF authentication: Session + Token
- CSP locked down to `'self'` for scripts/styles/images/fonts/connect
- HTTPS-only cookies and HSTS **enabled in production**

---

## 🧪 Usage

- **Admin**: `http://localhost:8000/admin`
- **Tokens** (optional): `POST /api-token-auth/` to obtain auth token
- **API base**: consider `api/` prefix in your `urls.py`

Example: authorize with token
```bash
curl -H "Authorization: Token <your-token>" http://localhost:8000/api/policies/
```

---

## 🗂️ Data Model Highlights

### Policies (`policies.Policy`)
- `contract_id`: auto (`P00001`, …)
- `product_name` → auto-assigns `product_code` (`200` Affinity, `300` Funeral)
- **Derived**:
  - `contract_premium` = monthly rate × period length (`M/Q/H/Y`)
  - `total_premium_due`, `months_paid`, `months_in_arrears`
  - `policy_status` (Accepted/Active/Lapsed/NTU)
  - `overall_policy_status` (Death/Cancelled/Active/…)
  - `claim_*` and `cancellation_*` convenience properties

### Receipts (`receipts.PremiumReceipt`)
- Auto `receipt_number` (`Rec000001`)
- Atomic update to policy totals
- Delete recalculates policy totals safely

### Claims (`claims.Claim`)
- Documents: `claim_form` (required), `burial_order` or `death_certificate`
- Statuses: `REQUESTED`, `APPROVED`, `REJECTED`, `PAID`
- `approve(approver=user)` sets `approved_by/approved_at`
- Optional email to Finance on approval

### Cancellations (`cancellations.CancellationRequest`)
- Statuses: `REQUESTED`, `APPROVED`
- Validates effective date and ensures policy is active

### Billing (`billing.BillingRecord`)
- One record per `(policy, billing_month)`
- Statement export CSV/PDF

### Commissions (`commissions.CommissionRecord`)
- One record per `(policy, commission_month)`
- Monthly commission rate = monthly premium × 10%
- Export CSV/PDF or email statement to agent

---

## 📚 API Documentation

> **Auth**: By default, endpoints require authentication (`IsAuthenticated`). Some list endpoints may be relaxed to `IsAuthenticatedOrReadOnly` if you enable it.

### Agents
- **List/Create**: `GET/POST /api/agents/`
- **Update**: `PUT/PATCH /api/agents/{id}/`

Search fields: `agent_code`, `agent_name`, `agent_surname`, `branch`  
Ordering: `agent_code`, `agent_name`, `date_joining`

**Example: create agent**
```bash
curl -X POST http://localhost:8000/api/agents/ \
  -H "Authorization: Token <token>" -H "Content-Type: application/json" \
  -d '{
    "agent_name": "Talent",
    "agent_surname": "Phiri",
    "branch": "HARARE",
    "date_joining": "2025-10-01"
  }'
```

---

### Clients
- **Admin**-centric management (Django Admin).  
  If you expose DRF endpoints, mirror the agent pattern:
  - `GET/POST /api/clients/`
  - `GET/PUT/PATCH/DELETE /api/clients/{id}/`

Client code (`CC00000001`) generated automatically.

---

### Policies
- Suggested routing:
  - `GET/POST /api/policies/`
  - `GET/PUT/PATCH/DELETE /api/policies/{id}/`

**Derived values** (read‑only in admin): `contract_premium`, `total_premium_due`, `months_*`, statuses.

**Example: create policy**
```bash
curl -X POST http://localhost:8000/api/policies/ \
  -H "Authorization: Token <token>" -H "Content-Type: application/json" \
  -d '{
    "product_name": "FUNERAL",
    "proposal_sign_date": "2025-09-01",
    "start_date": "2025-10-01",
    "beneficiary_name": "Esnath",
    "beneficiary_id": "63-123456Z63",
    "agent": 1,
    "paypoint": 3,
    "client": 17,
    "cover": 1000,
    "frequency": "M"
  }'
```

---

### Receipts
- **List/Create**: `GET/POST /api/receipts/`  
- **Retrieve/Update/Delete**: `GET/PUT/PATCH/DELETE /api/receipts/{id}/`

On create, `receipted_by` is set to the current user. Policy totals update atomically.

**Example: receipting**
```bash
curl -X POST http://localhost:8000/api/receipts/ \
  -H "Authorization: Token <token>" -H "Content-Type: application/json" \
  -d '{ "policy": 42, "amount_received": "5.00" }'
```

---

### Claims
- **Submit**: `POST /api/claims/submit/`  
  Serializer requires `policy`, `claim_form`, and either `burial_order` or `death_certificate`.  
- **List Pending** (manager role): `GET /api/claims/pending/`  
- **Approve** (manager role): `POST /api/claims/{id}/approve/`

**Example: approve claim**
```bash
curl -X POST http://localhost:8000/api/claims/123/approve/ \
  -H "Authorization: Token <manager-token>" -H "Content-Type: application/json" \
  -d '{}'
```

> **Note**: Ensure your `IsManager` permission and email settings (`DEFAULT_FROM_EMAIL`) are configured for Finance notifications.

---

### Cancellations
- Managed via Admin actions; recommended DRF pattern (if exposed):
  - `POST /api/cancellations/{id}/approve/`

Validation ensures policy is **Active** and effective date is not in the past.

---

### Billing Statements
- **List saved**: `GET /api/billing-records/`
- **Active policies subset**: `GET /api/billing-records/active-policies/`
- **Statement**: `GET /api/billing-records/statement/?paypoint_id=<id>|paypoint_code=<code>|paypoint=<name>&month=YYYY-MM&export=json|csv|pdf`

**Example (CSV export)**:
```bash
curl -L "http://localhost:8000/api/billing-records/statement/?paypoint_code=ppszesa&month=2025-11&export=csv" \
  -H "Authorization: Token <token>" -o billing_ppszesa_nov-25.csv
```

---

### Commission Statements
- **List saved**: `GET /api/commissions/`
- **Statement**: `GET /api/commissions/statement/?agent_id=<id>|agent_code=<code>|agent=<name>&month=YYYY-MM&export=json|csv|pdf|email&save=true|false`

**Example (email to agent)**:
```bash
curl -X GET "http://localhost:8000/api/commissions/statement/?agent_code=A0001&month=2025-11&export=email&save=true" \
  -H "Authorization: Token <token>"
```

- Monthly rate conversion:
  - Frequency → months per period: `M=1, Q=3, H=6, Y=12`
  - **Monthly premium** = `contract_premium / months_in_period`
  - **Commission due** = `monthly_premium × 0.10`

---

## 🔐 Security & Compliance
- **CSP**: Scripts, styles, fonts, images restricted to `'self'`.
- **Cookies/SSL**: `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, and `SECURE_SSL_REDIRECT` in **production**.
- **HSTS**: Preload + include subdomains (1 year).
- **Headers**: `X_FRAME_OPTIONS=DENY`, `SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_BROWSER_XSS_FILTER=True`.
- **Passwords**: Django validators enabled.

---

## 🛡️ Admin Workflows

### Upload Approval (Agents/Clients/Policies/Receipts)
- Approve/reject upload batches with admin actions.
- On approval, `process_upload(upload)` handles ingestion; messages display any row‑level errors.

### Claims Approval
- Approve selected **Pending Claims**; system sets `approved_by/approved_at`.
- Optional: send **Finance** payment requisition email.

### Cancellations Approval
- Approve **Pending Cancellation** requests; validation ensures dates and status integrity.

### Billing & Commission Exports
- Admin actions and API endpoints produce **CSV**/**PDF** with totals and clear headers.

---

## ✅ Pre‑Deployment Checklist
- **Routes**: Ensure all API routes are registered in `urls.py` (ViewSets/APIs).
- **Permissions**:
  - Verify `IsManager` and role mapping for claims approval.
  - Confirm DRF default permissions as intended (`IsAuthenticatedOrReadOnly` vs `IsAuthenticated`).
- **Email**:
  - Set `DEFAULT_FROM_EMAIL` and SMTP backend (not console) in production.
- **Database**:
  - Switch from SQLite → **PostgreSQL** (recommended).
- **Consistency**:
  - Standardize `related_name` across `Upload` models.
  - Fix minor typos (e.g., `list_disply` → `list_display`).
  - Align claims views that reference `Policy.PolicyState.ACTIVE` with the actual policy status implementation.
- **Security**:
  - Configure `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`.
  - Review CSP directives if you add external assets.

---

## 🔮 Future Enhancements
- **JWT** authentication for mobile clients.
- **Role‑based access control (RBAC)** with granular permissions.
- **Dashboards**: KPIs for persistency, collections, claims turnaround.
- **Payment integrations**: USSD, mobile money, card payments.
- **Data imports**: Bulk policy and receipt loads with dry‑run & error reporting.
- **Observability**: Request/response logging, alerts.

---

## 📄 License
Proprietary — intended for internal use within **your company**.  
If you plan to open source, replace this section with the appropriate license (e.g., MIT).

---

### 🧷 Appendix — Sample `urls.py`
```python
# life_admin_system/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from billing.views import BillingRecordViewSet
from commissions.views import CommissionRecordViewSet
from agents.views import AgentListCreateAPIView, AgentDetailAPIView
from receipts.views import (
    PremiumReceiptListCreateAPIView, PremiumReceiptRetrieveUpdateDestroyAPIView,
    UploadListCreateAPIView, UploadRetrieveUpdateDestroyAPIView
)
from claims.views import SubmitClaimAPIView, PendingClaimsAPIView, ApproveClaimAPIView

router = DefaultRouter()
router.register(r'billing-records', BillingRecordViewSet, basename='billing-records')
router.register(r'commissions', CommissionRecordViewSet, basename='commissions')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # Agents
    path('api/agents/', AgentListCreateAPIView.as_view(), name='agent-list-create'),
    path('api/agents/<int:pk>/', AgentDetailAPIView.as_view(), name='agent-detail'),

    # Receipts
    path('api/receipts/', PremiumReceiptListCreateAPIView.as_view(), name='receipt-list-create'),
    path('api/receipts/<int:pk>/', PremiumReceiptRetrieveUpdateDestroyAPIView.as_view(), name='receipt-rud'),

    # Uploads (example: receipts uploads)
    path('api/uploads/', UploadListCreateAPIView.as_view(), name='upload-list-create'),
    path('api/uploads/<int:pk>/', UploadRetrieveUpdateDestroyAPIView.as_view(), name='upload-rud'),

    # Claims
    path('api/claims/submit/', SubmitClaimAPIView.as_view(), name='claim-submit'),
    path('api/claims/pending/', PendingClaimsAPIView.as_view(), name='claims-pending'),
    path('api/claims/<int:pk>/approve/', ApproveClaimAPIView.as_view(), name='claim-approve'),
]
```

---
