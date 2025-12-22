# Qdrant Deployment Guide for Railway

This guide walks through deploying Qdrant on Railway and migrating from pgvector.

## Benefits of Qdrant

- **10x faster** vector similarity search
- **No format bugs** (proper SDK handles serialization)
- **Better scaling** for large datasets
- **Simple** - just works without format quirks

---

## Step 1: Deploy Qdrant on Railway

### Option A: Using Railway Template (Easiest)

1. Go to Railway Dashboard
2. Click **"New Project"**
3. Select **"Deploy from Docker Image"**
4. Enter image: `qdrant/qdrant:latest`
5. Railway will automatically deploy

### Option B: Manual Deployment

1. Create new service in Railway
2. Add from Docker Image: `qdrant/qdrant:latest`
3. Set PORT (Railway provides this automatically)
4. Add persistent volume:
   - Mount path: `/qdrant/storage`
   - Size: 1GB (should be enough for thousands of users)

### Configuration

Qdrant automatically exposes:
- HTTP API on port `6333` (or `$PORT` in Railway)
- gRPC on port `6334`

No additional environment variables needed!

---

## Step 2: Get Qdrant URL

After deployment, Railway provides:
- **Private URL** (within Railway network): `http://qdrant.railway.internal:6333`
- **Public URL** (if needed): `https://qdrant-xxxx.railway.app`

**Use the private URL** for better performance and security.

---

## Step 3: Set Environment Variable

In your **backend service** on Railway:

```bash
QDRANT_URL=http://qdrant.railway.internal:6333
```

Or if using public URL:
```bash
QDRANT_URL=https://qdrant-xxxx.railway.app
```

---

## Step 4: Deploy Backend Code

The backend automatically detects `QDRANT_URL` and uses Qdrant instead of pgvector.

```bash
git push origin main
```

Railway will automatically redeploy your backend.

---

## Step 5: Migrate Existing Embeddings

After backend is deployed, run the migration script:

### If you have Railway CLI:

```bash
# SSH into backend service
railway run python migrate_to_qdrant.py --user-id YOUR_USER_ID

# Or migrate all users
railway run python migrate_to_qdrant.py
```

### Without Railway CLI:

1. **Option A**: Add migration as a startup task (one-time)
   - Create a temporary endpoint that triggers migration
   - Call it once, then remove it

2. **Option B**: Run locally with Railway connection
   ```bash
   # Set environment variables locally
   export QDRANT_URL=https://qdrant-xxxx.railway.app  # Use public URL
   export OPENAI_API_KEY=sk-...
   export SUPABASE_URL=https://...
   export SUPABASE_SERVICE_ROLE_KEY=...

   # Run migration
   python migrate_to_qdrant.py --user-id YOUR_USER_ID
   ```

---

## Step 6: Verify Migration

Check logs for:
```
✅ All embeddings successfully migrated to Qdrant!
```

Test semantic search:
```bash
python migrate_to_qdrant.py --user-id YOUR_USER_ID --verify-only
```

Expected output:
```
✅ Found 3 results:
1. Question: Tell me about yourself...
   Similarity: 0.9234
```

---

## Troubleshooting

### Connection Error

```
Error: Could not connect to Qdrant at http://qdrant.railway.internal:6333
```

**Solution**: Make sure both services are in the same Railway project. Railway's internal networking only works within the same project.

### No Results Found After Migration

```
⚠️  No results found. This might indicate an issue.
```

**Check**:
1. Did migration complete successfully?
2. Are embeddings in Qdrant?
   ```python
   qdrant.get_collection_info()
   # Should show: points_count > 0
   ```

3. Check Qdrant logs in Railway dashboard

### Format Errors

```
TypeError: 'str' object is not subscriptable
```

**Solution**: Embeddings might be stored as strings in Supabase. The migration script handles this automatically. Check migration logs.

---

## Architecture After Migration

```
┌─────────────────┐
│    Frontend     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backend API    │
└────┬───────┬────┘
     │       │
     │       └──────────────────┐
     ▼                          ▼
┌─────────────┐       ┌──────────────────┐
│  Supabase   │       │     Qdrant       │
│             │       │                  │
│ • User data │       │ • Vector search  │
│ • Q&A text  │       │ • Embeddings     │
│ • Profiles  │       │ • 10x faster     │
└─────────────┘       └──────────────────┘
     │                         ▲
     │                         │
     └─────────────────────────┘
          Auto-sync via API
```

**Data Flow**:
1. User creates/updates Q&A → Supabase (source of truth)
2. Background job → Generate embedding
3. Auto-sync → Qdrant (search index)
4. Search query → Qdrant (fast)
5. Return results → Backend → Frontend

---

## Monitoring

### Check Qdrant Health

```bash
curl http://qdrant.railway.internal:6333/health
# or visit https://qdrant-xxxx.railway.app/dashboard
```

### Check Collection Stats

In your backend code:
```python
from app.services.qdrant_service import get_qdrant_service

qdrant = get_qdrant_service(
    qdrant_url=settings.QDRANT_URL,
    openai_api_key=settings.OPENAI_API_KEY
)

info = qdrant.get_collection_info()
print(f"Points: {info['points_count']}")
print(f"Vectors: {info['vectors_count']}")
```

### Railway Metrics

Railway dashboard shows:
- **CPU usage** (should be very low)
- **Memory usage** (typically < 100MB)
- **Network traffic**

---

## Cost Estimate

**Railway Pricing** (usage-based):
- Qdrant with 1GB volume: ~$5-10/month
- Very low CPU/memory usage
- Most cost is from persistent storage

**Total additional cost**: ~$10/month

**Trade-off**:
- No more pgvector format bugs
- 10x faster search
- Better developer experience

**Worth it!**

---

## Rollback Plan (If Needed)

If something goes wrong:

1. Remove `QDRANT_URL` environment variable
2. Backend automatically falls back to pgvector
3. Re-deploy backend
4. Old pgvector search still works

**Data is safe**: Supabase is still the source of truth.

---

## Future Improvements

### Add PostgreSQL Trigger for Auto-Sync

Instead of background tasks in API, use Supabase triggers:

```sql
CREATE OR REPLACE FUNCTION notify_qdrant_sync()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('qdrant_sync', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER qa_pairs_qdrant_sync
AFTER INSERT OR UPDATE ON qa_pairs
FOR EACH ROW
EXECUTE FUNCTION notify_qdrant_sync();
```

Then run a background listener that syncs to Qdrant.

### Enable Qdrant Authentication

For production:
```bash
QDRANT_API_KEY=your-secret-key
```

Update backend config to use API key.

---

## Summary

✅ Deploy Qdrant on Railway
✅ Set `QDRANT_URL` environment variable
✅ Deploy backend (auto-detects Qdrant)
✅ Run migration script
✅ Verify search works
✅ Monitor in Railway dashboard

**Result**: 10x faster vector search, no format bugs, happy developers!
