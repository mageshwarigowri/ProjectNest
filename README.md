# ProjectNest

ProjectNest is a modern full-stack ecommerce prototype for curated technology project kits. It combines a React/Vite storefront, a Django REST API, inventory-aware ordering, reward coins, shipment tracking, invoice generation, and a Groq-powered assistant restricted to store topics.

## What is included

- Responsive light/dark storefront with 10 project categories and 100 realistic seeded products
- Search, category filters, sorting, ratings, discount pricing, and stock labels
- Guest checkout plus username/password accounts
- Persistent authenticated cart and browser-local guest cart
- Customer, inventory manager, and administrator roles
- Atomic stock updates that prevent overselling
- Flat ₹99 shipping, free above ₹1,999, and tax-inclusive INR pricing
- Order emails through Gmail SMTP, shipment history, and downloadable PDF invoices
- Reward coins: earn one per ₹100 after delivery; redeem up to 20% of a later order
- Django Admin plus role-protected product CRUD and CSV import/export APIs
- Session-scoped chatbot history in the browser, 20 guest questions per hour, and a larger authenticated allowance
- Catalog-grounded Groq answers with deterministic rejection of unrelated questions
- SQLite for the simplest local setup and PostgreSQL-ready production settings
- Docker Compose, Render backend blueprint, and Vercel SPA configuration

## Architecture

```text
React/Vite storefront (5173)
        │ JSON + JWT
        ▼
Django REST API (8000) ── Groq API
        │                 Gmail SMTP
        ▼
SQLite locally / PostgreSQL in production
```

The Groq key is used only by Django. It is never sent to or bundled into the React application.

## Local setup

Prerequisites: Python 3.12+, Node.js 20+, and npm.

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_store
python manage.py runserver
```

Open `backend/.env` and add `GROQ_API_KEY`. Without it, the assistant runs in a safe catalog-grounded demo mode so the rest of the site remains testable.

The seed command creates a development administrator:

- Username: `admin`
- Password: `ChangeMe123!`

Change that password immediately with `python manage.py changepassword admin`.

### 2. Frontend

In a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173). Django Admin is at [http://localhost:8000/admin](http://localhost:8000/admin).

## Environment variables

All secrets belong in `backend/.env`, which Git ignores. Never prefix backend secrets with `VITE_`.

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django signing secret; use a strong random value in production |
| `DATABASE_URL` | SQLite locally or PostgreSQL connection URL |
| `FRONTEND_URLS` | Comma-separated permitted storefront origins |
| `GROQ_API_KEY` | Groq server-side API key |
| `GROQ_MODEL` | Defaults to `llama-3.3-70b-versatile` |
| `EMAIL_HOST_USER` | Gmail address used for order emails |
| `EMAIL_HOST_PASSWORD` | Gmail App Password, not the normal account password |
| `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` | Reserved payment credentials; COD works locally by default |
| `CLOUDINARY_URL` | Production media account configuration |

For Gmail, enable two-step verification and create an App Password. If SMTP variables are empty, local order emails print safely in the backend console.

## Inventory and roles

Create inventory managers in Django Admin, then set their profile role to `Inventory manager`. They can update products through the API and import/export CSV data:

- `POST /api/inventory/import/` — multipart CSV with a `file` field
- `GET /api/inventory/export/` — download the current catalog

The accepted CSV header is:

```text
category,sku,name,slug,short_description,description,price,discount_percent,stock,image_url
```

Low-stock and out-of-stock items are highlighted in the storefront and Django Admin. Shipment events can be added inline to an order. Changing an order to `delivered` awards reward coins once.

## Chatbot safety boundary

The assistant uses three layers:

1. A deterministic topic gate rejects clearly unrelated requests before contacting Groq.
2. Relevant products and current stock are fetched from the database for every question.
3. A low-temperature system instruction requires answers to use only store policy and live catalog context.

The chatbot cannot view private order data or perform cart actions. Guest usage is limited to 20 questions per hour per session; signing in raises the allowance. Conversation messages exist only in React state and disappear when the browser session ends.

## Tests and production build

```powershell
cd backend
python manage.py test

cd ..\frontend
npm run build
```

## Docker

After optionally creating `backend/.env`:

```powershell
docker compose up --build
```

The storefront runs at `http://localhost`; the API runs at `http://localhost:8000`.

## Recommended deployment

1. Push the repository to GitHub.
2. Create the Django/PostgreSQL services on Render using `render.yaml`.
3. Add `ALLOWED_HOSTS`, `FRONTEND_URLS`, `GROQ_API_KEY`, Gmail credentials, and optional Cloudinary/Razorpay values in Render.
4. Run `python manage.py seed_store` once from the Render shell.
5. Import `frontend` into Vercel and set `VITE_API_URL=https://YOUR-RENDER-SERVICE.onrender.com/api` before building.
6. Update Render's `FRONTEND_URLS` to the assigned Vercel URL.

No custom domain is required; the Render and Vercel provided domains are sufficient for this prototype.

## Prototype payment note

Cash on delivery is fully usable in the local prototype. The Razorpay credentials and dependency are prepared for the production integration, but real payment capture and webhook verification should be completed and tested in Razorpay Test Mode before accepting any real payment.
