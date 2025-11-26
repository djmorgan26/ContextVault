# Context Vault - Deployment Guide

## Deployment Architecture

```
Frontend (Vercel)                    Backend (Render)                Database (Railway)
contextvault.vercel.app       contextvault-api.onrender.com       Postgres Ohio
     │                                  │                               │
     ├─ Auto-deploy from main          ├─ Auto-deploy from main         ├─ Persistent storage
     ├─ Environment variables          ├─ Docker container              ├─ Daily backups
     └─ Edge CDN                       └─ Health checks                 └─ SSL connection
```

## Prerequisites

- GitHub account (for code repository)
- Vercel account (frontend hosting)
- Render account (backend hosting)
- Railway account ✅ (database hosting - already set up)
- Google OAuth credentials ✅ (already created)

---

## Database Setup (Railway) ✅

**Already configured:**
- Service: context-vault-postgres
- Database: contextvaultdb
- User: [Your database user]
- External URL: `postgresql://user:password@host:5432/database_name`

**To run migrations:**
```bash
cd backend
export DATABASE_URL="postgresql://user:password@host:5432/database_name"
alembic upgrade head
```

---

## Backend Deployment (Render)

### 1. Create New Web Service

1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect GitHub repository: `djmorgan26/ContextVault`
4. Configure:
   - **Name**: `contextvault-api`
   - **Region**: Ohio (same as database)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free

### 2. Environment Variables

Add in Render dashboard:

```bash
# App Config
APP_SECRET_KEY=<generate with: openssl rand -base64 32>
JWT_SECRET_KEY=<generate with: openssl rand -base64 32>
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:password@host:5432/database_name

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your-client-secret
GOOGLE_OAUTH_REDIRECT_URI=https://contextvault-api.onrender.com/api/auth/google/callback

# Epic (sandbox for now)
EPIC_CLIENT_ID=your-epic-client-id
EPIC_REDIRECT_URI=https://contextvault-api.onrender.com/api/integrations/epic/callback
EPIC_FHIR_BASE=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4

# Ollama (future: point to hosted Ollama instance)
OLLAMA_HOST=http://localhost:11434
EPHEMERAL_CONTAINER_ENABLED=false  # Disable for MVP (no Docker in Render free tier)

# CORS
ALLOWED_ORIGINS=https://contextvault.vercel.app,http://localhost:5173
```

### 3. Health Check

Render will automatically check `/health` endpoint every 30 seconds.

### 4. Deploy

Click "Create Web Service" → Render builds and deploys automatically.

**Expected URL**: `https://contextvault-api.onrender.com`

---

## Frontend Deployment (Vercel)

### 1. Import GitHub Repository

1. Go to https://vercel.com/new
2. Import `djmorgan26/ContextVault`
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### 2. Environment Variables

Add in Vercel dashboard:

```bash
VITE_API_BASE_URL=https://contextvault-api.onrender.com
VITE_GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

### 3. Deploy

Click "Deploy" → Vercel builds and deploys automatically.

**Expected URL**: `https://contextvault.vercel.app`

### 4. Update Google OAuth Redirect URIs

Go back to Google Cloud Console and add production URLs:
- https://contextvault-api.onrender.com/api/auth/google/callback
- https://contextvault.vercel.app (authorized JavaScript origin)

---

## Continuous Deployment

Both services auto-deploy on push to `main`:

```
git push origin main
  ↓
GitHub webhook triggers
  ↓
├─ Vercel rebuilds frontend (2-3 minutes)
└─ Render rebuilds backend (3-5 minutes)
  ↓
Deployments live!
```

### Deployment Checklist

Before merging to main:
- [ ] All tests pass locally
- [ ] No console errors in frontend
- [ ] Backend health check works
- [ ] Database migrations ready
- [ ] Environment variables documented

---

## Database Migrations (Production)

**Run migrations before deploying code changes:**

```bash
# Connect to Railway database
export DATABASE_URL="postgresql://user:password@host:5432/database_name"

# Run pending migrations
cd backend
alembic upgrade head

# Verify
alembic current
```

**Rollback if needed:**
```bash
alembic downgrade -1  # Go back one migration
```

---

## Monitoring & Observability

### Render Logs

View in dashboard: https://dashboard.render.com/web/YOUR_SERVICE/logs

**Or via CLI:**
```bash
npm install -g render-cli
render login
render logs contextvault-api --tail
```

### Vercel Logs

View in dashboard: https://vercel.com/YOUR_PROJECT/deployments

### Railway Database Metrics

View in dashboard: https://railway.app/project/YOUR_PROJECT

Metrics:
- CPU usage
- Memory usage
- Connection count
- Query performance

---

## Performance Optimization

### Render Free Tier Limitations

**Cold Starts:**
- Service spins down after 15 minutes of inactivity
- First request takes ~30 seconds to wake up

**Solution:**
- Upgrade to paid plan ($7/mo for always-on)
- Or: Use cron-job.org to ping `/health` every 10 minutes

### Vercel Edge Caching

Add cache headers for static assets:

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu']
        }
      }
    }
  }
});
```

### Database Connection Pooling

```python
# backend/app/core/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=5,           # Railway free tier max 10 connections
    max_overflow=5,        # Allow 5 more if needed
    pool_pre_ping=True,    # Verify connection before use
    pool_recycle=3600      # Recycle after 1 hour
)
```

---

## Security Hardening (Production)

### SSL/TLS

- ✅ Vercel: Automatic Let's Encrypt certificates
- ✅ Render: Automatic SSL for .onrender.com domain
- ✅ Railway: SSL required for database connections

### Secrets Management

**Never commit to git:**
- `APP_SECRET_KEY`
- `JWT_SECRET_KEY`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `DATABASE_URL` password

**Rotate secrets:**
- Annually: `APP_SECRET_KEY`, `JWT_SECRET_KEY`
- After breach: Immediately
- On team member departure: Within 24 hours

### Rate Limiting

Already configured in backend (see `api_endpoints.md`):
- 10 req/min for auth endpoints
- 100 req/min for vault
- 20 req/min for chat

### CORS

Only allow production frontend:
```python
allow_origins=["https://contextvault.vercel.app"]
```

---

## Backup & Recovery

### Database Backups

Railway provides automated backups:
- Frequency: Daily
- Retention: 7 days (free tier)
- Manual backup: Export via CLI

**Manual backup:**
```bash
pg_dump -h your-db-host \
        -U your-db-user \
        -d your-database-name \
        -F c \
        -f backup_$(date +%Y%m%d).dump
```

**Restore:**
```bash
pg_restore -h your-db-host \
           -U your-db-user \
           -d your-database-name \
           --clean \
           backup_20250125.dump
```

### Disaster Recovery Procedure

**Scenario: Database corrupted**

1. Stop backend service (prevent more writes)
2. Restore from Railway backup (via dashboard)
3. Verify data integrity
4. Restart backend service
5. Monitor for errors

**RTO (Recovery Time Objective)**: 1 hour
**RPO (Recovery Point Objective)**: 24 hours (last backup)

---

## Scaling Plan

### Current (MVP - 0-1000 users)

```
Frontend: Vercel Free ($0/mo)
Backend: Render Free ($0/mo) - Spins down after inactivity
Database: Railway Free ($0/mo) - 1GB storage
Total: $0/mo
```

**Limitations:**
- Cold starts (~30s)
- 1GB database storage
- No real-time features
- Single backend instance

### Phase 2 (1000-10,000 users)

```
Frontend: Vercel Pro ($20/mo)
Backend: Render Standard ($7-25/mo) - Always on
Database: Railway Pro ($20/mo) - 8GB storage
Total: ~$50/mo
```

**Improvements:**
- No cold starts
- More database storage
- Better support

### Phase 3 (10,000+ users)

```
Frontend: Vercel Pro ($20/mo)
Backend: Multiple Render instances ($100+/mo) + Load balancer
Database: Railway with read replicas ($100+/mo)
Redis: Upstash ($10/mo) - Caching
Total: ~$250/mo
```

**Features:**
- Horizontal scaling
- Read replicas for performance
- Redis caching
- Background job workers

---

## Troubleshooting

### Backend won't start

**Check logs:**
```bash
render logs contextvault-api --tail
```

**Common issues:**
- Missing environment variable (check Render dashboard)
- Database connection failed (verify DATABASE_URL)
- Port binding error (Render sets $PORT automatically, use it)

### Frontend shows API errors

**Check:**
1. Backend is running: `curl https://contextvault-api.onrender.com/health`
2. CORS configured: Backend allows `contextvault.vercel.app`
3. API URL correct: Check `VITE_API_BASE_URL` in Vercel

### Database connection timeout

**Causes:**
- Too many connections (check Railway metrics)
- SSL mode wrong (must be `require` for Railway)
- Firewall blocking (Railway is public, shouldn't block)

**Fix:**
```python
# Add to DATABASE_URL
DATABASE_URL=postgresql://...?sslmode=require
```

---

## Deployment Commands Cheat Sheet

```bash
# Local development
docker-compose up                    # Start all services
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Deploy
git push origin main                 # Auto-deploys to Vercel + Render

# View logs
render logs contextvault-api --tail
vercel logs contextvault

# Database backup
pg_dump -h your-db-host -U your-db-user your-database-name > backup.sql
```

---

**Next Steps:**
1. Deploy backend to Render
2. Deploy frontend to Vercel
3. Run database migrations
4. Test production deployment end-to-end
5. Set up health check monitoring
