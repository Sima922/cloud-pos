# ☁️ Cloud POS

> A multi-tenant, web-based Point of Sale system built with Django  designed for small to medium businesses to process sales, manage inventory, and generate insights in real time.


**🔗 Live Demo:** [https://clouds-pos.onrender.com/login/](https://clouds-pos.onrender.com/login/)

| Demo Credentials | Email | Password |
|---|---|---|
| Admin (Full Access) | `admintest@gmail.com` | `admin10@2025` |
| Cashier (Limited Access) | `cashiertest@gmail.com` | `cashier@2025` |

> ⚠️ Demo credentials are sandboxed accounts for testing only. Please do not store real business data in the demo environment.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Data Models](#data-models)
- [Authentication & Authorization](#authentication--authorization)
- [REST API Reference](#rest-api-reference)
- [Local Development Setup](#local-development-setup)
- [Environment Variables](#environment-variables)
- [Deployment (Render)](#deployment-render)
- [Screenshots](#screenshots)
- [Roadmap](#roadmap)
- [License](#license)
- [Contact](#contact)

---

## Overview

Cloud POS is a subscription-based, multi-tenant Point of Sale platform. Each business (subscription) operates in full data isolation  products, orders, customers, and reports are all scoped to the owning subscription. The system supports multiple user roles under a single subscription, making it suitable for businesses with owners, admins, and cashier staff.

**Who is it for?** Retail shops, restaurants, or any SMB needing a cloud-based POS without the cost of enterprise software.

**The core problem it solves:** Most affordable POS tools are either desktop-locked or lack proper multi-user role management. Cloud POS is browser-based, role-aware, and deployable in minutes.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, Django 4.x, Django REST Framework |
| **Database** | PostgreSQL (production), SQLite (local dev) |
| **Frontend** | Bootstrap 5, Chart.js, Vanilla JS |
| **Auth** | Django session auth + DRF `IsAuthenticated` |
| **Exports** | ReportLab (PDF), openpyxl (Excel), Python csv |
| **Static Files** | Whitenoise |
| **Hosting** | Render (web service + managed PostgreSQL) |
| **Process Manager** | Gunicorn |

---

## Architecture

### Architecture

![Architecture](docs/screenshots/Pos_Architecture.png)

---

**Key architectural decision — Subscription Scoping:**
Every view, queryset, and API endpoint resolves the current user's `ClientSubscription` before querying data. This ensures complete data isolation between different business tenants using the same deployment.

```python
def get_user_subscription(user):
    sub = getattr(user, 'subscription', None)
    if sub:
        return sub
    return getattr(user, 'owned_subscription', None)
```

This utility function is the foundation of multi-tenancy across `accounts`, `sales`, `products`, and `reports` apps.

---

## Key Features

### 🛒 Point of Sale (POS)
- Real-time product grid with live stock indicators
- Cart management: add, remove, and update quantities
- Configurable tax rate and percentage-based discounts
- Multiple payment methods: Cash, Card, Bank Transfer, Mobile Payment
- Automatic change calculation
- Receipt generation in HTML (printable)
- Customer association (walk-in or registered customer)

### 📦 Product Management
- Full CRUD for products, scoped to subscription
- Category filtering and text search
- Low-stock alerts based on configurable reorder levels
- Paginated product list (20 per page)
- Stock automatically decremented on order completion

### 📊 Analytics & Reports
- Sales dashboard with configurable date ranges (Today / Last 7 Days / Last 30 Days / Custom)
- Key metrics: Total Sales, Total Orders, Average Order Value, Items Sold
- Interactive Chart.js line chart (sales trend) and doughnut chart (top categories)
- Top 5 products and categories by revenue
- Export engine supporting CSV, PDF (ReportLab), and Excel (openpyxl)

### 👥 Multi-User & Multi-Tenant
- Owner, Admin, and Cashier roles with enforced permissions
- Each subscription has a configurable user limit
- Admins can register new users under their own subscription
- Superusers can manage across all subscriptions

### 💱 Currency Configuration
- Configurable currency symbol, decimal places, and thousand separator
- Currency applied consistently across all views, exports, and receipts via a shared `format_currency()` utility

---

## Data Models

```
ClientSubscription
│   ├── business_name
│   ├── active (bool)
│   ├── user_limit
│   └── owner (FK → User)
│
User
│   ├── email (login identifier)
│   ├── role: owner | admin | cashier
│   └── subscription (FK → ClientSubscription)
│
Product
│   ├── name, price, stock, reorder_level
│   ├── is_active
│   ├── category (FK → Category)
│   └── subscription (FK → ClientSubscription)
│
Order
│   ├── status: pending | completed
│   ├── total, tax_rate, discount
│   ├── amount_paid, change_given
│   ├── payment_method
│   ├── customer (FK → Customer, nullable)
│   ├── user (FK → User)
│   └── subscription (FK → ClientSubscription)
│
OrderItem
│   ├── quantity, price
│   ├── order (FK → Order)
│   └── product (FK → Product)
│
Customer
│   ├── name, email, phone
│   └── subscription (FK → ClientSubscription)
```

---

## Authentication & Authorization

### Login
Authentication uses Django's built-in `authenticate()` and `login()` with email as the username field, managed by `CustomLoginView`.

### Role-Based Access Control (RBAC)

| Feature | Owner | Admin | Cashier |
|---|:---:|:---:|:---:|
| POS Transactions | ✅ | ✅ | ✅ |
| Add / Edit Products | ✅ | ✅ | ❌ |
| Delete Products | ✅ | ✅ | ❌ |
| View Analytics | ✅ | ✅ | Limited |
| Export Reports | ✅ | ✅ | ❌ |
| Register New Users | ✅ | ✅ | ❌ |
| Manage Subscription | ✅ | ❌ | ❌ |

Permissions are enforced using Django's `UserPassesTestMixin` on class-based views and `IsAuthenticated` on DRF API views. Admins are automatically granted `is_staff = True` on registration. User creation is gated by the subscription's `user_limit`.

---

## REST API Reference

Base URL: `/api/`  All endpoints require session authentication.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/orders/` | List orders for current subscription |
| `POST` | `/api/orders/` | Create and complete a new order |
| `GET` | `/api/orders/<id>/` | Retrieve a specific order |
| `PUT/PATCH` | `/api/orders/<id>/` | Update an order |
| `DELETE` | `/api/orders/<id>/` | Delete an order |
| `GET` | `/api/test-auth/` | Verify auth status and subscription |
| `GET` | `/api/debug-orders/` | Debug view of orders for subscription |
| `GET` | `/sales/receipt/<id>/` | Generate receipt (HTML or JSON) |

### Order Creation Payload
```json
POST /api/orders/
{
  "customer": 5,
  "tax_rate": 8.0,
  "discount": 10.0,
  "amount_paid": 500.00,
  "payment_method": "cash",
  "items": [
    { "product": 12, "quantity": 2, "price": 199.99 }
  ]
}
```

On creation, the API automatically sets `status = 'completed'`, calculates `total` and `change_given`, and calls `update_inventory()` to decrement product stock.

### Receipt Endpoint
```
GET /sales/receipt/<order_id>/?format=html   → Printable HTML receipt

```

---

## Local Development Setup

### Prerequisites
- Python 3.10+
- pip
- PostgreSQL (or SQLite for local dev)
- Git

```bash
# 1. Clone the repository
git clone https://github.com/Sima922/cloud-pos.git
cd cloud-pos/cloud_pos

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template and fill in your values
cp .env.example .env

# 5. Apply database migrations
python manage.py migrate

# 6. Create a superuser
python manage.py createsuperuser

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Run the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

---

## Environment Variables

Create a `.env` file in the project root.

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | `django-insecure-xxxx...` |
| `DEBUG` | Debug mode (`True` in dev only) | `False` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `clouds-pos.onrender.com` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `CURRENCY_SYMBOL` | Currency symbol displayed in UI | `P` |
| `CURRENCY` | ISO currency code | `BWP` |
| `THOUSAND_SEPARATOR` | Enable thousands separator | `True` |
| `DECIMAL_PLACES` | Number of decimal places | `2` |

---

## Deployment (Render)

Cloud POS is deployed as a **Web Service** on [Render](https://render.com) with a managed PostgreSQL database.

### Build Command
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

### Start Command
```bash
gunicorn cloud_pos.wsgi:application
```

### Static Files
Whitenoise serves static files directly from Django — no separate CDN or S3 bucket required.

```python
# settings.py
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    ...
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## Screenshots

### POS Interface
![POS Interface](docs/screenshots/pos.png)

### Reports Dashboard
![Reports Dashboard](docs/screenshots/reports.png)

### Product Management
![Product Management](docs/screenshots/products.png)

### Receipt
![Receipt](docs/screenshots/receipt.png)

---

## Roadmap

### Near Term
- [ ] Unit and integration test suite
- [ ] Barcode scanner support for product lookup
- [ ] Low-stock email/SMS notifications
- [ ] Profit margin tracking per product

### Medium Term
- [ ] **Offline Mode** — Service worker for processing sales without internet
- [ ] **Automated Reordering** — Smart inventory replenishment triggers
- [ ] **Supplier Management** — End-to-end procurement tracking


### Long Term
- [ ] **AI-Powered Demand Forecasting** — Predict stock needs with ML
- [ ] **Customer Segmentation** — Purchase history-driven marketing
- [ ] **Accounting Integrations** — QuickBooks and Xero API connectors
- [ ] **Employee Performance Dashboards** — Per-cashier sales analytics
- [ ] **Barcode & Inventory Upgrade** — Full warehouse management support

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## Contact & Support

| Channel | Details |
|---|---|
| 📞 Call / WhatsApp | +267 716 19313 |
| 📧 Email | tbsmesh10@gmail.com |



