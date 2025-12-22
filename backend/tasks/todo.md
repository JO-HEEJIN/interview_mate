# Qdrant Integration - Post Deployment Tasks

## Problem
Qdrant is now deployed on Railway, but the backend needs to be configured to use it and existing embeddings need to be migrated from pgvector.

## To-Do List

- [ ] 1. Set QDRANT_URL environment variable in Railway backend service
- [ ] 2. Redeploy backend to pick up the new environment variable
- [ ] 3. Verify backend starts successfully and Qdrant connection works
- [ ] 4. Run migration script to move embeddings from Supabase to Qdrant
- [ ] 5. Test semantic search with Qdrant
- [ ] 6. Commit the graceful fallback fix

## Implementation Notes

### Step 1: Set QDRANT_URL
In Railway dashboard, go to backend service and add:
```
QDRANT_URL=http://qdrant.railway.internal:6333
```
(Use Railway internal URL for better performance and security)

### Step 2: Redeploy
Railway will automatically redeploy when env var is added.

### Step 3: Verify
Check logs for:
```
Initialized ClaudeService with Qdrant for vector search
```

### Step 4: Migration
Run the migration script:
```bash
railway run python migrate_to_qdrant.py --user-id <your-user-id>
```

### Step 5: Test
Test semantic search via API to verify it returns results.

### Step 6: Commit
Commit the graceful fallback changes with a clean message.

## Review
(Will be filled after completion)
