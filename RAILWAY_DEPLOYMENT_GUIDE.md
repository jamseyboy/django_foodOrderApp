# 🚂 Railway Deployment Guide — Food Order App (Backend + Frontend)

This guide walks through deploying **both** services for the Food Order App on [Railway](https://railway.app):

1. **`django_foodOrderApp`** — Django Ninja API (Docker-based)
2. **PostgreSQL** — managed database for the API
3. **`nextjs_foodOrderApp`** — Next.js frontend

By the end, you'll have a live backend URL, a live frontend URL, and the two talking to each other over HTTPS.

---

## 0. Prerequisites

- A [Railway](https://railway.app) account (sign in with GitHub is easiest)
- Both repos pushed to your own GitHub account:
  - `django_foodOrderApp`
  - `nextjs_foodOrderApp`
- The Railway CLI is optional but handy: `npm install -g @railway/cli`

---

## 1. Create a Railway Project

1. Go to [railway.app/new](https://railway.app/new).
2. Click **"New Project"**.
3. You'll add services into this one project so they can share environment variables and an internal network. Keep the project open — you'll add three services to it: Postgres, the Django API, and the Next.js app.

---

## 2. Deploy PostgreSQL

1. Inside the project, click **"+ New"** → **"Database"** → **"Add PostgreSQL"**.
2. Railway provisions a Postgres instance automatically and creates a `DATABASE_URL` variable on that service.
3. Click into the Postgres service → **"Variables"** tab and copy the `DATABASE_URL` value (you'll reference it from the Django service in the next step). It looks like:
   ```
   postgresql://postgres:<password>@<host>.railway.internal:5432/railway
   ```
   > Use the **internal** `railway.internal` host (not the public proxy host) when connecting from another Railway service in the same project — it's faster and free of egress charges.

---

## 3. Deploy the Django Backend

### 3.1 Create the service

1. In the same project, click **"+ New"** → **"GitHub Repo"** → select your `django_foodOrderApp` repo.
2. Railway will detect the `railway.toml` in the repo root, which tells it to build using the included `Dockerfile`:
   ```toml
   [build]
   builder = "DOCKERFILE"
   dockerfilePath = "./Dockerfile"
   ```
   No changes needed here — Railway will build the Docker image automatically on every push.

### 3.2 Set environment variables

Click into the new service → **"Variables"** tab → add the following:

| Variable | Value |
|---|---|
| `DJANGO_SECRET_KEY` | A long random string. Generate locally with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DJANGO_DEBUG` | `False` |
| `DATABASE_URL` | Reference the Postgres service instead of pasting the value: click **"Add Reference"** → select the Postgres service → `DATABASE_URL`. This keeps it in sync automatically. |
| `CORS_ALLOWED_ORIGINS` | Leave blank for now — you'll fill this in once the frontend has a URL (Step 5.4) |

> Railway automatically injects a `PORT` variable — the Dockerfile's startup script already reads it (`RUN_PORT="${PORT:-8000}"`), so you don't need to set it yourself.

### 3.3 Generate a public domain

1. Go to **"Settings"** tab of the Django service → **"Networking"** → **"Generate Domain"**.
2. Railway gives you a URL like:
   ```
   https://django-foodorderapp-production.up.railway.app
   ```
3. This domain is already covered by the app's `ALLOWED_HOSTS` setting (`.railway.app`) and `CSRF_TRUSTED_ORIGINS`, so no code changes are needed.

### 3.4 Deploy & verify

1. Railway deploys automatically after you add the service. Watch the **"Deployments"** tab for build/runtime logs.
2. On container start, the entrypoint script runs `python manage.py migrate --no-input` automatically, then starts `gunicorn`.
3. Once it's live, verify with:
   ```bash
   curl https://<your-backend-domain>.up.railway.app/api/hello
   # → "Hello World"
   ```
4. (Optional) Create an admin user so you can use `/admin/`. Since you don't have a local terminal into the container by default, use the Railway CLI:
   ```bash
   railway link        # link this directory to your Railway project
   railway run python src/manage.py createsuperuser
   ```
   Or open a one-off shell via **Railway dashboard → service → "..." menu → "Run command"**.

---

## 4. Deploy the Next.js Frontend

### 4.1 Create the service

1. Back in the same Railway project: **"+ New"** → **"GitHub Repo"** → select `nextjs_foodOrderApp`.
2. Railway auto-detects Next.js (via Nixpacks) and sets sensible defaults:
   - Build command: `npm run build`
   - Start command: `npm run start`

   No `Dockerfile` is required for this repo — Nixpacks handles it. If you'd rather use a Dockerfile for consistency with the backend, that also works, but it isn't necessary.

### 4.2 Set environment variables

Go to **"Variables"** tab and add:

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_DJANGO_BASE_URL` | The backend's public Railway domain from Step 3.3, e.g. `https://django-foodorderapp-production.up.railway.app` (no trailing slash) |

> Because this variable is read at **build time** (Next.js inlines `NEXT_PUBLIC_*` vars into the client bundle), make sure it's set **before** the first deploy. If you add or change it later, trigger a redeploy so the value gets baked into a new build.

### 4.3 Generate a public domain

Same as the backend: **Settings → Networking → Generate Domain**. You'll get something like:
```
https://nextjs-foodorderapp-production.up.railway.app
```

### 4.4 Deploy & verify

Railway builds and deploys automatically. Once live, open the generated URL in your browser — you should see the app's home page.

---

## 5. Connect the Two Services

### 5.1 Point the frontend at the backend
Already done in Step 4.2 (`NEXT_PUBLIC_DJANGO_BASE_URL`).

### 5.2 Allow the frontend's origin in the backend's CORS settings
Go back to the **Django service → Variables** and set:

```
CORS_ALLOWED_ORIGINS=https://nextjs-foodorderapp-production.up.railway.app
```

(Comma-separate multiple origins if you also want to allow `localhost:3000` for local testing against the prod API.)

Redeploy the backend (Railway redeploys automatically when you save a variable) and you're done.

### 5.3 Test end-to-end
Open the frontend URL, navigate to **Foods** or **Orders**, and confirm data loads from the live API (check the browser dev tools Network tab for `200` responses from your backend domain, with no CORS errors in the console).

---

## 6. Custom Domains (Optional)

For each service: **Settings → Networking → Custom Domain → add your domain**, then create the CNAME record Railway shows you at your DNS provider.

If you add a custom domain to the backend, also add it to `CSRF_TRUSTED_ORIGINS` and `ALLOWED_HOSTS` in `src/foodOrderApp/settings.py` (currently hard-coded to `.railway.app`), e.g.:

```python
ALLOWED_HOSTS = [".railway.app", "api.yourdomain.com"]
CSRF_TRUSTED_ORIGINS = [
    "http://*.railway.app",
    "https://*.railway.app",
    "https://api.yourdomain.com",
]
```
Commit and push — Railway redeploys automatically.

---

## 7. Ongoing Deploys

Both services auto-deploy on every push to the connected branch (default `main`). To deploy a different branch or roll back:

- **Deployments tab → select a previous deployment → "Redeploy"** to roll back.
- **Settings → Source → change branch** to deploy from a different branch.

---

## 8. Environment Variable Summary

### Backend (`django_foodOrderApp`)
```env
DJANGO_SECRET_KEY=<random-secret>
DJANGO_DEBUG=False
DATABASE_URL=<reference to Postgres service>
CORS_ALLOWED_ORIGINS=https://<your-frontend-domain>.up.railway.app
```

### Frontend (`nextjs_foodOrderApp`)
```env
NEXT_PUBLIC_DJANGO_BASE_URL=https://<your-backend-domain>.up.railway.app
```

---

## 9. Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Frontend shows network errors / failed fetches | `NEXT_PUBLIC_DJANGO_BASE_URL` missing or wrong, or set after build | Set the variable, then trigger a fresh deploy (not just a restart) |
| CORS error in browser console | Frontend origin missing from `CORS_ALLOWED_ORIGINS` | Add the exact frontend URL (with `https://`, no trailing slash) and redeploy backend |
| `Bad Request (400)` on every backend request | Frontend or custom domain not in `ALLOWED_HOSTS` | Add the domain to `ALLOWED_HOSTS` in `settings.py` and redeploy |
| Backend crashes on boot referencing database | `DATABASE_URL` not set / Postgres service not linked | Re-check the variable reference in Step 3.2 |
| 502 from Railway on the backend | App isn't binding to Railway's `$PORT` | Already handled by the Dockerfile's `paracord_runner.sh` — confirm you haven't overridden the start command in Railway settings |
| Migrations not applied | N/A — they run automatically on every container start (`migrate --no-input`) | Check deployment logs for migration errors |

---

## Architecture Recap

```
┌─────────────────────┐        HTTPS        ┌──────────────────────┐
│  Next.js Frontend    │ ───────────────────▶│  Django Ninja API     │
│  (Railway service)   │   /api/...           │  (Railway service,    │
│  NEXT_PUBLIC_DJANGO_  │ ◀───────────────────│   Dockerfile + gunicorn)│
│  BASE_URL             │      JSON            └──────────┬───────────┘
└─────────────────────┘                                  │
                                                           │ internal network
                                                           ▼
                                                ┌──────────────────────┐
                                                │  PostgreSQL            │
                                                │  (Railway service)     │
                                                └──────────────────────┘
```

All three services live in one Railway project, so the Postgres connection uses Railway's private internal network, while the frontend and backend talk to each other over their public HTTPS domains.
