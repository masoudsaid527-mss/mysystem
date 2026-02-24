# Deploy Guide (Render)

## 1) Push code to GitHub
- Ensure this project is in one GitHub repository.
- Commit the new files: `render.yaml`, `Procfile`, `.env.example`.

## 2) Create services on Render
- In Render, choose **New +** -> **Blueprint**.
- Connect your GitHub repository.
- Render will detect `render.yaml` and create:
- `hostel-backend` (Python web service)
- `hostel-frontend` (Static site)
- `hostel-db` (PostgreSQL)

## 3) Set required environment variables
- On `hostel-backend`:
- `DJANGO_ALLOWED_HOSTS=hostel-backend.onrender.com`
- `FRONTEND_URL=https://hostel-frontend.onrender.com`
- `CORS_ALLOWED_ORIGINS=https://hostel-frontend.onrender.com`
- `CSRF_TRUSTED_ORIGINS=https://hostel-frontend.onrender.com,https://hostel-backend.onrender.com`
- `SESSION_COOKIE_SAMESITE=None`
- `CSRF_COOKIE_SAMESITE=None`
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_SSL_REDIRECT=True`

- On `hostel-frontend`:
- `VITE_API_BASE=https://hostel-backend.onrender.com`
- `VITE_ROUTER_BASENAME=/`

## 4) Redeploy
- Trigger redeploy for both services after env vars are set.

## 5) Verify login/register flow
- Open frontend URL.
- Register a new student.
- Login with that account.
- Confirm backend session cookie exists and `/api/me/` returns 200.
