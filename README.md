# 🍔 Food Order App — Backend (Django + Django Ninja)

A REST API for a restaurant food-ordering system, built with **Django 5** and **Django Ninja**. It manages food items, customers, orders, and order items, and exposes a JWT-secured JSON API consumed by the [Next.js frontend](https://github.com/jamseyboy/nextjs_foodOrderApp.git).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.1 + [django-ninja](https://django-ninja.dev/) / `ninja-extra` |
| Auth | `django-ninja-jwt` (JWT access/refresh tokens) |
| Database | SQLite (local dev) / PostgreSQL (production, via `dj-database-url`) |
| CORS | `django-cors-headers` |
| WSGI server | `gunicorn` |
| Container | Docker (single image, migrate-then-serve entrypoint) |
| Hosting | [Railway](https://railway.app) |

---

## Project Structure

```
django_foodOrderApp-main/
├── Dockerfile               # Production image (gunicorn + migrate-on-boot)
├── railway.toml             # Railway build config (Dockerfile builder)
├── rav.yaml                 # Convenience task runner (rav) — dev shortcuts
├── requirements.txt         # Python dependencies
└── src/
    ├── manage.py
    ├── db.sqlite3            # Local dev database (not used in production)
    ├── foodOrderApp/         # Project config
    │   ├── settings.py
    │   ├── urls.py            # mounts api/ -> foodOrderApp/api.py
    │   ├── api.py              # NinjaExtraAPI root: JWT controller, /hello, /me
    │   └── wsgi.py / asgi.py
    ├── food/                  # Food catalog app
    │   ├── models.py           # foodModel
    │   ├── api.py               # /api/food/...
    │   └── schemas.py
    └── customer/              # Customers, Orders, Order Items
        ├── models.py           # customerModel, orderModel, orderItemModel
        ├── api.py               # /api/customer/...
        └── schemas.py
```

---

## Prerequisites

- Python **3.12+**
- pip
- (Optional) Docker, if you want to run the production-style container locally
- (Optional) PostgreSQL, if you don't want to use the default SQLite dev DB

---

## 1. Local Setup

```bash
# Clone
git clone https://github.com/jamseyboy/django_foodOrderApp.git
cd django_foodOrderApp

# Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file **in the project root** (same level as `requirements.txt`, *not* inside `src/`):

```env
DJANGO_SECRET_KEY=replace-with-a-long-random-string
DJANGO_DEBUG=True
DATABASE_URL=
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

| Variable | Required | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | ✅ | Django cryptographic signing key. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DJANGO_DEBUG` | ✅ | `True` locally, **must be `False` in production** |
| `DATABASE_URL` | ❌ (local) / ✅ (prod) | Leave empty to fall back to local SQLite. In production, set to a Postgres connection string, e.g. `postgresql://user:pass@host:5432/dbname` |
| `CORS_ALLOWED_ORIGINS` | ✅ | Comma-separated list of origins allowed to call the API, e.g. your frontend URL |

> ⚠️ When `DJANGO_DEBUG=True`, `ALLOWED_HOSTS` is automatically opened to `["*"]`. In production it's restricted to `*.railway.app` (see the Railway guide if you use a custom domain).

### Run migrations & start the server

```bash
cd src
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin access
python manage.py runserver
```

The API is now live at **http://localhost:8000/api/**. Django admin is at **http://localhost:8000/admin/**.

> The repo also ships a `rav.yaml` with shortcuts if you have the [`rav`](https://pypi.org/project/rav/) task runner installed: `rav server`, `rav migrate`, `rav makemigrations`, `rav createsuperuser`, `rav shell`.

---

## 2. API Reference

All routes are mounted under `/api/`.

### Auth (JWT — `ninja-jwt`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/token/pair` | Obtain access + refresh tokens (`{"username": "...", "password": "..."}`) |
| `POST` | `/api/token/refresh` | Refresh an access token |
| `GET` | `/api/me` | Get current authenticated user (requires `Authorization: Bearer <token>`) |
| `GET` | `/api/hello` | Health check, returns `"Hello World"` |

### Food (`/api/food/`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `food_info_all` | List all food items |
| `GET` | `todays_food` | List food items created today |
| `POST` | `create_food` | Create a food item — `{"food_name": "Pizza", "food_price": 500}` |

### Customer & Orders (`/api/customer/`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `customer_info_all` | List all customers |
| `POST` | `create_customer` | `{"username": "john_doe"}` |
| `GET` | `food_info_all` | List all food items (duplicate convenience route) |
| `GET` | `orderslist` | List all orders |
| `POST` | `create_orders` | `{"customer_id": 1, "order_status": "pending"}` |
| `POST` | `create_order_item` | Add items to an order — see payload below |
| `POST` | `update_order_status` | `{"id": 1, "order_status": "delivered"}` |
| `GET` | `todays_detail_order_list` | Today's orders grouped by customer name |

`create_order_item` payload:
```json
{
  "order_id": 1,
  "order_status": "confirmed",
  "items": [
    { "food_id": 1, "food_quantity": 2 }
  ]
}
```

---

## 3. Data Models

```
customerModel
  └── username

orderModel
  ├── customer_info  -> FK customerModel
  ├── order_status
  └── timestamp

orderItemModel
  ├── order_info  -> FK orderModel
  ├── food_info   -> FK foodModel
  ├── food_quantity
  ├── total_amount
  └── timestamp

foodModel
  ├── food_name
  ├── food_price
  └── timestamp
```

---

## 4. Running with Docker (locally)

```bash
docker build -t food-order-backend .

docker run -p 8000:8000 \
  -e DJANGO_SECRET_KEY=your-secret-key \
  -e DJANGO_DEBUG=False \
  -e DATABASE_URL=postgresql://user:password@host:5432/db \
  -e CORS_ALLOWED_ORIGINS=http://localhost:3000 \
  food-order-backend
```

The Dockerfile builds a Python 3.12 image, installs dependencies, and at **container start** (not build time) runs `python manage.py migrate --no-input` followed by `gunicorn foodOrderApp.wsgi:application`, binding to `$PORT` (defaults to 8000). This is exactly what Railway runs in production.

---

## Deployment

This project is pre-configured for **Railway** (`railway.toml` + `Dockerfile`). See **[`../RAILWAY_DEPLOYMENT_GUIDE.md`]([../RAILWAY_DEPLOYMENT_GUIDE.md](https://github.com/jamseyboy/django_foodOrderApp/blob/main/RAILWAY_DEPLOYMENT_GUIDE.md))** for the full step-by-step guide covering both this backend and the Next.js frontend.

---

## Testing

```bash
cd src
python manage.py test
```

---

## Tech Notes

- Timezone is set to `Asia/Kolkata` (`TIME_ZONE` in `settings.py`) — adjust if deploying for a different region.
- CORS is currently wide open (`CORS_ALLOW_ALL_ORIGINS = True`) for `/api/*` routes, in addition to the explicit `CORS_ALLOWED_ORIGINS` list. Tighten this for production by setting `CORS_ALLOW_ALL_ORIGINS = False` once your frontend domain is finalized.
- `db.sqlite3` is for local development only — Railway/production use Postgres via `DATABASE_URL`.

---

## License

MIT
