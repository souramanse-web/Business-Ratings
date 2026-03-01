# Release Notes

## v1.0.0 - 2026-03-01

### Highlights
- Production-ready Flask business rating platform deployed successfully.
- Render blueprint deployment added with managed PostgreSQL support.
- Health monitoring endpoint added and verified.
- Admin workflow validated end-to-end.
- Rating submission flow fixed and verified.

### Shipped Changes
- Added cloud deployment config:
  - `render.yaml`
  - `Procfile`
- Updated app configuration to support `DATABASE_URL` with SQLite fallback for local development.
- Added health endpoint:
  - `GET /healthz` returns `{ "status": "ok" }`
- Added production dependencies:
  - `gunicorn`
  - `psycopg2-binary`
- Removed obsolete stock chatbot feature and related files.
- Improved mobile responsiveness across templates.
- Fixed `/api/rate` to robustly parse `business_id` and `score` input types.

### Validation Summary
- Local test suite passing (`pytest`): 3 passed.
- Local health check passing: `/healthz` => 200 + `{"status":"ok"}`.
- Live Render health endpoint verified green.
- Login, admin dashboard access, and rating submission verified successfully.

### Operational Notes
- Keep Render Deploy Hook URL private.
- Recommended: configure weekly database backup/export.
- Recommended: set up custom domain + HTTPS redirect in Render.

### Key Commits Included
- `94db09e` Fix rating API type handling for score and business_id
- `b81fdb5` Add Render deploy hook instructions to README
- `723a994` Prepare cloud deploy on Render and clean app scope
- `34d09ca` Update branding, logo integration, and UI adjustments
- `80fa6e9` Update UI branding, floating elements, and bank data
