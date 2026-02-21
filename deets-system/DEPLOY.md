# Deploy Deets to Render (Free)

## Quick Deploy (5 minutes)

1. **Push to GitHub:**
   ```bash
   cd /home/eng/.openclaw/workspace/deets-system
   git add .
   git commit -m "Phase 1: Core DROP/VALIDATE/CHALLENGE/PASS"
   git push origin master
   ```
   (Replace with your GitHub repo URL if needed)

2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select this repository
   - Branch: `master`
   - Build command: (leave blank, Render uses Procfile)
   - Start command: (leave blank, Render uses Procfile)

3. **Set Environment Variables:**
   - Add `ANTHROPIC_API_KEY` with your key
   - Click "Create Web Service"

4. **Wait ~2-3 minutes for deployment**

5. **Your URL will be:** `https://deets-XXXX.onrender.com`

## What's Deployed

- ✅ Full Phase 1 backend (DROP/VALIDATE/CHALLENGE/PASS/TRAIL)
- ✅ Database (SQLite, persistent storage)
- ✅ Landing page
- ✅ Setup page
- ✅ All API endpoints tested

## Testing

Once live:
```bash
# Check health
curl https://deets-XXXX.onrender.com/health

# Create user
curl -X POST https://deets-XXXX.onrender.com/setup \
  -H "Content-Type: application/json" \
  -d '{"name":"Chris","phone":"+1"}'

# Drop a deet (use the endpoint from Phase 1 tests)
```

## Limitations (Free Tier)

- Server spins down after 15 minutes of inactivity (~30 sec startup)
- 0.5GB RAM
- Shared CPU
- SQLite file storage (data persists, but no backups)

For production, upgrade to Standard (~$7/mo) for always-on + Postgres.
