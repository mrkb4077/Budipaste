# 🚀 CLOUD DEPLOYMENT - QUICK START (5 STEPS)

## Step 1: Prepare GitHub Repository (5 min)
```bash
# Go to GitHub and create new repo: https://github.com/new
# Name it: Budipaste (make it PUBLIC)

cd C:\Users\yiliy\BudipasteProject
git init
git add .
git commit -m "Initial Budipaste FastAPI deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/Budipaste.git
git push -u origin main
```

## Step 2: Deploy to Railway (3 min)
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub"
4. Select your "Budipaste" repository
5. Click "Deploy Now"
6. **Wait 3 minutes for deployment**

## Step 3: Get Your Backend URL (2 min)
1. In Railway dashboard, click your project
2. Click "Settings" tab
3. Copy **Domain** URL (format: `https://budipaste-xyz.railway.app`)
4. **Save this URL**

## Step 4: Add Railway Environment Variables (3 min)
In Railway dashboard, navigate to **Variables** tab and add:

```
SECRET_KEY = PJUnllsGB5uQdBJChm7NQqdUFDdgMlK3omy2IVErQE0
BACKEND_CORS_ORIGINS = ["https://bjz5m74f.budibase.app"]
ENVIRONMENT = production
DEBUG = False
```
Click **Save** (auto-redeploys in 1 minute)

## Step 5: Connect to Budibase Cloud (10 min)

### 5A: Login to Budibase Cloud
- Go to https://bjz5m74f.budibase.app/
- Login with your credentials

### 5B: Create New App
1. Click "Create New App"
2. Name: **Live**
3. Click "Create"

### 5C: Add REST API Connection
1. Go to **"Data"** panel (left sidebar)
2. Click **"Add data source"** → **"REST API"**
3. Fill:
   - **Name:** `Budipaste API`
   - **URL:** `https://your-railway-domain.railway.app/api/v1`
4. Click **"Save"**

### 5D: Test Connection (Get Bearer Token)
```bash
# Generate JWT token
curl -X POST https://your-railway-domain.railway.app/api/v1/auth/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=TestPass123!"

# Copy the token from response
```

### 5E: Add Authentication
1. In Budibase Data panel, click **"Budipaste API"**
2. Click **"Authentication"** tab
3. Choose **"Bearer Token"**
4. Paste your JWT token
5. Click **"Save"**

### 5F: Create First Query
1. Click **"+"** to create new query
2. **Type:** REST
3. **Data source:** Budipaste API
4. **Method:** GET
5. **URL:** `/participants/`
6. Click **"Run query"** → ✅ Should see participants data

### 5G: Build First Screen
1. Go to **"Screen"** tab
2. Click **"+"** to create new screen
3. Name: **Participants**
4. Drag **"Data table"** component
5. Link to your participants query
6. Click **"Publish"**

**✅ DONE! Your app is live at:** https://bjz5m74f.budibase.app/app/live

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **404 Backend** | Verify Railway domain is correct and deployment completed |
| **CORS Error** | Check BACKEND_CORS_ORIGINS includes https://bjz5m74f.budibase.app |
| **Bearer Token Failed** | Generate new token using curl command above |
| **No Data in Table** | Verify participants query runs successfully with "Run query" button |

---

## Key URLs Reference

| Item | URL |
|------|-----|
| **Railway Dashboard** | https://railway.app |
| **Your Backend** | `https://your-railway-domain.railway.app` |
| **Budibase Cloud** | https://bjz5m74f.budibase.app/ |
| **Auth Endpoint** | `https://your-railway-domain.railway.app/api/v1/auth/access-token` |
| **Full Guide** | See CLOUD_DEPLOYMENT_GUIDE.md |

---

## Generated SECRET_KEY (Use in Step 4)
```
PJUnllsGB5uQdBJChm7NQqdUFDdgMlK3omy2IVErQE0
```

---

## Next Apps to Build
After "Live" app works:
- [ ] Attendance → `/attendance/` 
- [ ] Plans → `/plans/`
- [ ] Activity Log → `/activities/`
- [ ] Roll Call → `/enrolments/`

Same pattern for each: Add data source → Create query → Build screen → Publish
