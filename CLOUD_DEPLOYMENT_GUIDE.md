# 🚀 FULL CLOUD SETUP GUIDE - Budipaste + Budibase Cloud

## Overview
This guide will help you deploy your FastAPI backend to the cloud and connect it to Budibase Cloud (bjz5m74f.budibase.app).

**Architecture:**
- **Backend:** FastAPI deployed on Railway.app
- **Frontend:** Budibase Cloud (https://bjz5m74f.budibase.app/)
- **Database:** SQLite on Railway (auto-persisted)
- **Authentication:** JWT Bearer tokens

---

## PART 1: Deploy FastAPI to Railway.app

### Step 1.1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub/Google account
3. Verify email

### Step 1.2: Connect GitHub Repository
1. In Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub"**
3. Authorize Railway to access GitHub
4. Fork or create new repository with your Budipaste code:
   - Navigate to: https://github.com/new
   - Repository name: `Budipaste`
   - Make it **Public** (required for free tier)
   - Create repository
   - Clone: `git clone https://github.com/YOUR_USERNAME/Budipaste.git`
   - Copy your BudipasteProject files into this repo
   - Push to GitHub:
     ```bash
     cd Budipaste
     git add .
     git commit -m "Initial Budipaste FastAPI deployment"
     git push origin main
     ```

### Step 1.3: Deploy from GitHub on Railway
1. In Railway, click **"New Project"** → **"Deploy from GitHub"**
2. Select your **Budipaste** repository
3. Railway automatically detects Python project
4. Click **"Deploy Now"**

**Wait 2-3 minutes for deployment to complete.**

### Step 1.4: Get Your Deployed URL
1. In Railway dashboard, click your deployed Budipaste project
2. Go to **"Settings"** tab → **"Domains"**
3. Copy the domain (format: `https://budipaste-xyz.railway.app`)
4. **Save this URL - you'll need it for Budibase configuration**

### Step 1.5: Configure Environment Variables on Railway
1. In Railway project, go to **"Variables"** tab
2. Add the following variables:

```
SECRET_KEY = Generate a random 32+ character string (e.g., use: python -c "import secrets; print(secrets.token_urlsafe(32))")
BACKEND_CORS_ORIGINS = ["https://bjz5m74f.budibase.app"]
DATABASE_URL = sqlite:///./budipaste_cloud.db
ENVIRONMENT = production
DEBUG = False
```

3. Click **"Save"** and the service will auto-redeploy

### Step 1.6: Verify Backend is Running
```bash
# Test your deployed backend
curl https://your-railway-domain.railway.app/
# Should return: {"message":"Welcome to the Budipaste API"}

# Test login endpoint
curl -X POST https://your-railway-domain.railway.app/api/v1/auth/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=TestPass123!"
# Should return JWT token
```

---

## PART 2: Update CORS in FastAPI Config

### Step 2.1: Update app/core/config.py
Update BACKEND_CORS_ORIGINS to include your cloud Budibase instance:

```python
BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
    "https://bjz5m74f.budibase.app",    # ✅ YOUR CLOUD BUDIBASE
    "http://localhost:3000",             # Local Budibase dev
    "http://localhost",                  # Local testing
    "http://127.0.0.1",                  # Local IP
]
```

After updating, commit and push to GitHub to auto-redeploy:
```bash
git add app/core/config.py
git commit -m "Add cloud Budibase CORS origin"
git push origin main
# Wait 2-3 minutes for Railway to auto-redeploy
```

---

## PART 3: Connect Budibase Cloud to Your Backend

### Step 3.1: Login to Budibase Cloud
1. Go to https://bjz5m74f.budibase.app/
2. Login with your credentials

### Step 3.2: Create a New App
1. Click **"Create New App"** (blue button)
2. Name: **Live** (your first app)
3. Click **"Create"**

### Step 3.3: Add REST API Data Source
1. In the app builder, go to **"Data"** panel (left sidebar)
2. Click **"Add data source"**
3. Select **"REST API"**
4. Configure:
   - **Name:** `Budipaste API`
   - **URL:** `https://your-railway-domain.railway.app/api/v1` (your deployed backend URL)
   - Click **"Save"**

### Step 3.4: Authenticate with Bearer Token
1. In Data panel, click your **"Budipaste API"** connection
2. Click **"Authentication"**
3. Choose **"Bearer Token"**
4. Token: Paste your JWT token (from curl test above)
5. Click **"Save"**

**To get a fresh JWT token:**
```bash
curl -X POST https://your-railway-domain.railway.app/api/v1/auth/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=TestPass123!"
```

### Step 3.5: Query Participants Endpoint (Test Connection)
1. In Data panel, click **"+"** to add new query
2. Type: **REST**
3. Data source: **Budipaste API**
4. Method: **GET**
5. URL: `/participants/`
6. Click **"Run query"**

**Success:** You should see list of participants in JSON format

---

## PART 4: Build First Screen in Budibase

### Step 4.1: Create Participants List Screen
1. In app builder, click **"Screen"** tab
2. Click **"+"** to create new screen
3. Name: **Participants**
4. Choose template: **"Form"** or **"Blank"**

### Step 4.2: Add Data Table Component
1. Drag **"Data table"** component to screen
2. Configure:
   - **Data source:** Select your participants query from Step 3.5
   - **Columns:** ID, First Name, Last Name, Email, Phone, Grade, etc.
3. Click **"Save"**

### Step 4.3: Add Create/Edit Form
1. Drag **"Form"** component below the table
2. Link to REST API:
   - **Form type:** Create
   - **Data source:** Budipaste API
   - **Method:** POST
   - **URL:** `/participants/`
   - **Fields:** Auto-fill from Pydantic schema
3. Click **"Save"**

### Step 4.4: Publish Your App
1. Click **"Publish"** (top right)
2. Your app is now live at: `https://bjz5m74f.budibase.app/app/live`

---

## PART 5: Create Remaining Apps

Repeat Steps 4.1-4.4 for:
- **Attendance** → `/attendance/` endpoint
- **Plans** → `/plans/` endpoint
- **Activity Log** → `/activities/` endpoint
- **Roll Call** → `/enrolments/` endpoint

---

## TROUBLESHOOTING

### 404 Not Found on Endpoints
✅ **Solution:** Ensure CORS is configured and backend is running on Railway

### CORS Error: "Access to XMLHttpRequest blocked"
✅ **Solution:** Add your Budibase domain to BACKEND_CORS_ORIGINS in FastAPI config

### Bearer Token Expired
✅ **Solution:** Generate new token:
```bash
curl -X POST https://your-railway-domain.railway.app/api/v1/auth/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=TestPass123!"
```

### Database Data Not Persisting
✅ **Solution:** Railway SQLite persists automatically. Check volume is mounted in Railway settings.

---

## Quick Reference

| Component | URL |
|-----------|-----|
| **Backend** | `https://your-railway-domain.railway.app` |
| **Budibase Cloud** | `https://bjz5m74f.budibase.app/` |
| **Auth Endpoint** | `https://your-railway-domain.railway.app/api/v1/auth/access-token` |
| **Participants API** | `https://your-railway-domain.railway.app/api/v1/participants/` |

---

## Next Steps After Cloud Deployment
1. ✅ Migrate remaining 4 apps from old Budibase (if data needed)
2. ✅ Configure user management and roles
3. ✅ Set up email notifications (optional)
4. ✅ Add data validation and error handling
5. ✅ Backup strategy (export data regularly from Budibase)

---

**Questions?** Check the Budibase docs: https://docs.budibase.com/
**Railway Docs:** https://docs.railway.app/
