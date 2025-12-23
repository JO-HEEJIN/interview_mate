# 🚀 InterviewMate.ai Deployment Guide (Last Updated: 2025-12-23)

## Overview

InterviewMate consists of two parts:
1. **Frontend** (Next.js) - Best deployed on Vercel
2. **Backend** (FastAPI) - Best deployed on Railway or Render

---

## Option 1: Vercel (Frontend) + Railway (Backend) - RECOMMENDED

### A. Deploy Backend to Railway

1. **Create Railway Account**: https://railway.app
2. **Install Railway CLI** (optional):
   ```bash
   npm i -g @railway/cli
   railway login
   ```

3. **Deploy via Dashboard**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select `interview_mate` repository
   - Set **Root Directory**: `backend`
   - Railway auto-detects Python and uses `pyproject.toml`

4. **Set Environment Variables** in Railway Dashboard:
   ```
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   SUPABASE_URL=https://awxhkdneruigroiitgbs.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
   SUPABASE_ANON_KEY=eyJhbGc...
   PORT=8000
   ```

5. **Custom Start Command** (if needed):
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

6. **Copy Backend URL**: e.g., `https://your-app.railway.app`

---

### B. Deploy Frontend to Vercel

1. **Create Vercel Account**: https://vercel.com

2. **Deploy via Vercel Dashboard**:
   - Click "Add New Project"
   - Import from GitHub
   - Select `interview_mate` repository
   - **Root Directory**: `frontend`
   - Framework Preset: Next.js (auto-detected)

3. **Environment Variables** in Vercel:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   NEXT_PUBLIC_WS_URL=wss://your-backend.railway.app/ws/transcribe
   NEXT_PUBLIC_SUPABASE_URL=https://awxhkdneruigroiitgbs.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
   NEXTAUTH_URL=https://your-app.vercel.app
   NEXTAUTH_SECRET=your-generated-secret
   ```

4. **Generate NEXTAUTH_SECRET**:
   ```bash
   openssl rand -base64 32
   ```

5. **Deploy**: Vercel will auto-deploy on git push

6. **Custom Domain** (optional):
   - Go to Project Settings → Domains
   - Add your custom domain (e.g., interviewmate.ai)

---

## Option 2: All-in-One Render Deployment

1. **Create Render Account**: https://render.com

2. **Connect GitHub**: 
   - Go to Dashboard
   - Connect your GitHub account

3. **Deploy using render.yaml**:
   - Render will auto-detect `render.yaml` in repo root
   - Or manually create two Web Services:
     - Backend: Python
     - Frontend: Node

4. **Set Environment Variables** for both services in Render Dashboard

5. **Deploy**: Push to GitHub, Render auto-deploys

---

## Option 3: Docker Deployment (Advanced)

### Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

ENV NODE_ENV=production
CMD ["npm", "start"]
```

### Deploy to any Docker platform (Fly.io, DigitalOcean, AWS ECS, etc.)

---

## Post-Deployment Checklist

### 1. Update Supabase Auth Settings

Go to Supabase Dashboard → Authentication → URL Configuration:

```
Site URL: https://your-frontend-domain.vercel.app
Redirect URLs:
  - https://your-frontend-domain.vercel.app/*
  - https://your-frontend-domain.vercel.app/interview
```

### 2. Update OAuth Providers

**Google Cloud Console**:
- Authorized redirect URIs:
  ```
  https://awxhkdneruigroiitgbs.supabase.co/auth/v1/callback
  ```

**GitHub OAuth App**:
- Homepage URL: `https://your-frontend-domain.vercel.app`
- Authorization callback URL:
  ```
  https://awxhkdneruigroiitgbs.supabase.co/auth/v1/callback
  ```

### 3. Update Frontend Metadata

Edit `frontend/src/app/layout.tsx`:

```typescript
export const metadata: Metadata = {
  // ...
  openGraph: {
    url: 'https://your-actual-domain.com', // Update this
    // ...
  },
};
```

### 4. Update Sitemap

Edit `frontend/public/sitemap.xml`:

Replace all `https://interviewmate.ai` with your actual domain.

### 5. CORS Configuration

Ensure backend allows frontend domain in CORS settings.

Edit `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend-domain.vercel.app",  # Add this
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6. Test Everything

- ✅ OAuth login (Google, GitHub)
- ✅ Resume upload
- ✅ Q&A generation
- ✅ Interview recording
- ✅ WebSocket connection

---

## Quick Deploy Commands

### Frontend (Vercel)
```bash
cd frontend
vercel
```

### Backend (Railway)
```bash
cd backend
railway up
```

---

## Environment Variables Reference

### Backend (.env)
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://awxhkdneruigroiitgbs.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_ANON_KEY=eyJ...
PORT=8000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_WS_URL=wss://your-backend.railway.app/ws/transcribe
NEXT_PUBLIC_SUPABASE_URL=https://awxhkdneruigroiitgbs.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXTAUTH_URL=https://your-frontend.vercel.app
NEXTAUTH_SECRET=random-32-char-string
```

---

## Monitoring & Logs

### Vercel
- Deployments: https://vercel.com/dashboard
- Logs: Real-time in dashboard
- Analytics: Built-in

### Railway
- Deployments: https://railway.app/dashboard
- Logs: Real-time in dashboard
- Metrics: CPU, Memory, Network

### Render
- Deployments: https://dashboard.render.com
- Logs: Real-time logs
- Metrics: Built-in monitoring

---

## Cost Estimates

### Free Tier Options

**Vercel**:
- Free: 100GB bandwidth, unlimited sites
- Pro: $20/mo per member

**Railway**:
- Free: $5 credit/month
- Usage-based: ~$5-10/month for small app

**Render**:
- Free: 750 hours/month (static sites free)
- Paid: $7/month for web service

**Recommended Setup (Free Tier)**:
- Frontend: Vercel (Free)
- Backend: Railway ($5-10/month)
- Database: Supabase (Free tier)
- Total: **~$5-10/month**

---

## Troubleshooting

### Frontend not connecting to backend
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify CORS settings in backend
- Check browser console for errors

### OAuth not working
- Verify redirect URLs in Supabase
- Check OAuth app settings (Google/GitHub)
- Ensure `NEXTAUTH_SECRET` is set

### WebSocket errors
- Use `wss://` not `ws://` for production
- Check backend WebSocket endpoint
- Verify firewall/proxy settings

### Database errors
- Check Supabase connection strings
- Verify service role key has permissions
- Check table permissions and RLS policies

---

## Next Steps After Deployment

1. **Set up monitoring**: Sentry, LogRocket, etc.
2. **Configure analytics**: Google Analytics, Plausible
3. **Set up CI/CD**: GitHub Actions for automated testing
4. **Enable caching**: Redis for performance
5. **Add rate limiting**: Protect APIs
6. **Set up backups**: Database backups
7. **Configure CDN**: CloudFlare for static assets

---

## Support

If you encounter issues:
1. Check deployment logs
2. Verify environment variables
3. Test locally first
4. Check this guide's troubleshooting section

Good luck with your deployment! 🚀
