# Heroku Deployment Guide for Civitas Demo

This guide provides step-by-step instructions for deploying the Civitas Demo application to Heroku.

## Architecture

The application is deployed as a single Heroku app where:
- FastAPI backend serves API endpoints at `/api/*`
- FastAPI also serves the built React frontend for all other routes
- PostgreSQL with PostGIS extension handles database operations
- Estimated cost: **$10-12/month** (Eco dyno + Essential-0 Postgres)

## Prerequisites

1. **Heroku CLI** installed - [Download here](https://devcenter.heroku.com/articles/heroku-cli)
2. **Git** repository initialized
3. **Anthropic API key** for the AI dispatcher feature
4. All code changes committed to git

## Deployment Steps

### Step 1: Heroku Setup

```bash
# Login to Heroku
heroku login

# Create new Heroku app (replace 'civitas-demo' with your preferred name)
heroku create civitas-demo

# Add PostgreSQL addon (Essential-0 plan: $5/month)
heroku addons:create heroku-postgresql:essential-0

# Configure buildpacks (order matters!)
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/python
```

### Step 2: Enable PostGIS Extension

```bash
# Connect to database
heroku pg:psql

# In the psql console, run:
CREATE EXTENSION IF NOT EXISTS postgis;
\dx  # Verify PostGIS is listed
\q   # Quit
```

### Step 3: Configure Environment Variables

```bash
# Application settings
heroku config:set APP_NAME="Civitas Demo"
heroku config:set DEBUG=False

# CORS - Replace with your actual Heroku app URL
heroku config:set ALLOWED_ORIGINS="https://civitas-demo.herokuapp.com"

# Generate a secure secret key
heroku config:set SECRET_KEY="$(openssl rand -hex 32)"

# AI API key - Replace with your actual Anthropic API key
heroku config:set ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxxx"

# Python path (for imports to work correctly)
heroku config:set PYTHONPATH=/app/backend

# Verify all configuration
heroku config
```

**Important**:
- Replace `civitas-demo.herokuapp.com` with your actual Heroku app domain
- Replace the ANTHROPIC_API_KEY with your real API key from [console.anthropic.com](https://console.anthropic.com/)

### Step 4: Deploy Application

```bash
# Ensure all changes are committed
git add .
git commit -m "Configure for Heroku deployment"

# Deploy to Heroku
git push heroku main

# If you're on a different branch (e.g., Claude-quick-build):
git push heroku Claude-quick-build:main

# Monitor deployment logs
heroku logs --tail
```

**What happens during deployment:**
1. Node.js buildpack runs `npm install` and `npm run build` → builds frontend to `frontend/dist/`
2. Python buildpack installs dependencies from `requirements.txt`
3. Release phase runs: `alembic upgrade head` (creates database tables)
4. Web dyno starts: FastAPI app on assigned port

### Step 5: Verify Deployment

```bash
# Check dyno status
heroku ps

# Test health endpoint
curl https://civitas-demo.herokuapp.com/health
# Expected: {"status":"healthy"}

# Open app in browser
heroku open
```

Visit these URLs to verify everything works:
- `https://your-app.herokuapp.com/` - React frontend
- `https://your-app.herokuapp.com/health` - Health check
- `https://your-app.herokuapp.com/docs` - API documentation

### Step 6: Seed Sample Data (Optional)

```bash
# Import sample crews
heroku run "cd backend && python scripts/import_crews_from_csv.py data/sample_crews.csv"

# Import sample tickets
heroku run "cd backend && python scripts/import_tickets_from_csv.py data/sample_tickets.csv"

# Verify data was imported
heroku pg:psql
SELECT COUNT(*) FROM tickets;
SELECT COUNT(*) FROM crews;
\q
```

## Files Created/Modified

### New Configuration Files

- **`Procfile`** - Defines web and release processes
- **`runtime.txt`** - Specifies Python 3.11.9
- **`requirements.txt`** - Root-level Python dependencies
- **`package.json`** - Root-level Node.js build configuration
- **`.slugignore`** - Excludes unnecessary files from deployment

### Modified Application Files

- **`backend/src/config.py`** - Handles Heroku's DATABASE_URL and postgres:// scheme conversion
- **`backend/src/main.py`** - Serves frontend static files from `frontend/dist/`
- **`frontend/src/services/api.ts`** - Uses same-origin API calls in production

## Post-Deployment Management

### View Logs

```bash
# Tail logs continuously
heroku logs --tail

# View last 200 lines
heroku logs -n 200

# Filter for errors
heroku logs --source app | grep ERROR
```

### Database Management

```bash
# Connect to database
heroku pg:psql

# Check migration status
heroku run "cd backend && alembic current"

# View migration history
heroku run "cd backend && alembic history"

# Create backup (recommended before migrations)
heroku pg:backups:capture

# Download backup
heroku pg:backups:download
```

### Scale Dynos

```bash
# Check current scaling
heroku ps

# Scale up for more capacity
heroku ps:scale web=2

# Scale down to save costs
heroku ps:scale web=1
```

## Troubleshooting

### Build Fails with "No module named 'src'"

**Solution**: Ensure PYTHONPATH is set correctly:
```bash
heroku config:set PYTHONPATH=/app/backend
heroku restart
```

### PostGIS Extension Not Found

**Solution**: Manually create the extension:
```bash
heroku pg:psql
CREATE EXTENSION IF NOT EXISTS postgis;
\q
```

### Frontend Shows Blank Page

**Solution**: Check that build completed successfully:
```bash
heroku run ls -la frontend/dist
```
Should show `index.html` and `assets/` directory.

### API Calls Fail with CORS Errors

**Solution**: Update ALLOWED_ORIGINS to match your domain:
```bash
# Get your app URL
heroku info | grep "Web URL"

# Update CORS setting
heroku config:set ALLOWED_ORIGINS="https://your-app.herokuapp.com"

# Restart dynos
heroku restart
```

### AI Dispatcher Not Working

**Solution**: Verify API key is set correctly:
```bash
heroku config:get ANTHROPIC_API_KEY
```
If empty or invalid, update it:
```bash
heroku config:set ANTHROPIC_API_KEY="your-actual-key"
heroku restart
```

### Database Connection Pool Exhausted

**Solution**: Either upgrade Postgres plan or reduce pool size:
```bash
# Option 1: Upgrade Postgres
heroku addons:upgrade heroku-postgresql:standard-0

# Option 2: Check connection pool settings in backend/src/database.py
```

## Cost Breakdown

**Monthly costs:**
- **Eco Dyno**: $5/month (or Basic: $7/month for better performance)
- **Essential-0 Postgres**: $5/month
- **Total**: $10-12/month

**Cost-saving tips:**
- Use Eco dynos for development/staging environments
- Scale down during off-hours if needed: `heroku ps:scale web=0`
- Consider free Papertrail addon for logging

## Updating the Application

When you make changes to your application:

```bash
# Commit your changes
git add .
git commit -m "Description of changes"

# Deploy to Heroku
git push heroku main

# Monitor the deployment
heroku logs --tail
```

The release phase will automatically run database migrations before the new code is deployed.

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Auto-set by Heroku Postgres addon | `postgres://...` |
| `APP_NAME` | Application name | `Civitas Demo` |
| `DEBUG` | Debug mode (should be False in production) | `False` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `https://your-app.herokuapp.com` |
| `SECRET_KEY` | Secret key for security | Generate with `openssl rand -hex 32` |
| `ANTHROPIC_API_KEY` | Anthropic API key for AI dispatcher | `sk-ant-...` |
| `PYTHONPATH` | Python import path | `/app/backend` |

## Support

For issues or questions:
- Check Heroku logs: `heroku logs --tail`
- Review application logs in `backend/logs/` (via `heroku run`)
- Verify environment variables: `heroku config`
- Test database connection: `heroku pg:psql`

## Next Steps

After successful deployment:

1. **Set up a custom domain** (optional):
   ```bash
   heroku domains:add www.yourdomain.com
   ```

2. **Enable automated backups**:
   ```bash
   heroku pg:backups:schedule --at '02:00 America/New_York' DATABASE_URL
   ```

3. **Set up monitoring**: Consider adding New Relic or Papertrail addons

4. **Configure CI/CD**: Set up GitHub Actions for automated deployments

Enjoy your deployed Civitas Demo application!
