# Railway Deployment Guide - Getting Your Live CFMP Website

## 🎯 Quick Overview
This guide walks you through deploying your CFMP Django application to Railway to get a live website URL for your professor.

**End Result:** `https://cfmp-production.up.railway.app` (your live website)

---

## 📋 Prerequisites Checklist
- [x] CFMP code implemented with Railway configuration
- [x] GitHub repository with your code
- [x] Railway account (free)
- [x] GitHub account connected to Railway

---

## 🚀 Step-by-Step Deployment Process

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Sign up with your **GitHub account** (recommended)
4. Verify your email if prompted

### Step 2: Create New Project from GitHub
1. In Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your **CIDM6325** repository
4. Select the **FALL2025** branch
5. Railway will automatically detect it's a Django project

### Step 3: Configure Environment Variables
Railway needs these environment variables set:

#### Required Variables:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
DJANGO_SETTINGS_MODULE=cfmp.settings.production
ALLOWED_HOSTS=cfmp-production.up.railway.app
```

#### How to Set Variables:
1. In your Railway project dashboard
2. Click on your **service** (should be auto-created)
3. Go to **"Variables"** tab
4. Add each variable:
   - **SECRET_KEY**: Generate at [Django Secret Key Generator](https://django-secret-key-generator.netlify.app/)
   - **DEBUG**: `False`
   - **DJANGO_SETTINGS_MODULE**: `cfmp.settings.production`
   - **ALLOWED_HOSTS**: Will be updated after deployment

### Step 4: Add PostgreSQL Database
1. In Railway project dashboard
2. Click **"New"** → **"Database"** → **"Add PostgreSQL"**
3. Railway automatically creates `DATABASE_URL` environment variable
4. Your Django app will automatically connect to this database

### Step 5: Deploy Your Application
1. Railway should automatically start deploying after GitHub connection
2. Watch the **"Deployments"** tab for build progress
3. Build process runs:
   - Installs dependencies from `requirements.txt`
   - Runs database migrations
   - Collects static files
   - Starts gunicorn server

### Step 6: Get Your Live URL
1. After successful deployment (green checkmark)
2. In Railway dashboard, find **"Domains"** section
3. Your URL will be something like: `https://cfmp-production.up.railway.app`
4. Click the URL to test your live website!

### Step 7: Update ALLOWED_HOSTS
1. Copy your Railway URL (from Step 6)
2. Go back to **"Variables"** tab
3. Update **ALLOWED_HOSTS** to: `your-app-name.up.railway.app`
4. Save - Railway will redeploy automatically

---

## 🔧 Troubleshooting Common Issues

### Issue: Build Failed
**Check:**
- Dependencies in `requirements.txt` are correct
- No syntax errors in Python code
- Railway build logs for specific errors

**Solution:**
```bash
# Check locally first
python manage.py check --deploy
python manage.py collectstatic --noinput
```

### Issue: Application Error (500)
**Check:**
- All environment variables are set correctly
- `SECRET_KEY` is set and valid
- `ALLOWED_HOSTS` includes your Railway domain

**Solution:**
1. Check Railway logs in "Deployments" → "View logs"
2. Verify environment variables
3. Test health check: `https://your-app.railway.app/health/`

### Issue: Database Connection Error
**Check:**
- PostgreSQL service is running in Railway
- `DATABASE_URL` environment variable exists
- No migration conflicts

**Solution:**
```bash
# Run migrations manually in Railway console
railway run python manage.py migrate
```

### Issue: Static Files Not Loading
**Check:**
- `collectstatic` runs successfully
- WhiteNoise is configured correctly
- Static files exist in repository

**Solution:** Verify in `cfmp/settings/production.py`:
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## 🎯 Testing Your Deployment

### Health Check
Visit: `https://your-app.railway.app/health/`

Should return:
```json
{
    "status": "healthy",
    "django_version": "5.2.6",
    "database": "healthy",
    "cache": "healthy"
}
```

### Admin Access
1. Visit: `https://your-app.railway.app/admin/`
2. Login with: `admin` / password you set
3. Verify admin interface works

### Core Functionality
1. Visit main page: `https://your-app.railway.app/`
2. Test navigation and basic features
3. Verify responsive design on mobile

---

## 📱 For Professor Demonstration

### What to Share:
- **Live URL**: `https://your-app.railway.app`
- **Admin URL**: `https://your-app.railway.app/admin/`
- **Health Check**: `https://your-app.railway.app/health/`

### Demo Points:
- ✅ Live, accessible website
- ✅ Professional hosting with HTTPS
- ✅ Database-backed functionality
- ✅ Responsive design
- ✅ Admin interface for content management
- ✅ Health monitoring and error tracking

---

## 🔄 Updating Your Deployment

### Automatic Updates (Recommended):
1. Push changes to **FALL2025** branch on GitHub
2. Railway automatically detects changes and redeploys
3. GitHub Actions runs tests before deployment
4. Monitor deployment in Railway dashboard

### Manual Deployment:
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Link project: `railway link`
4. Deploy: `railway up`

---

## 💰 Cost Information

### Railway Free Tier:
- **$5/month** in credits (sufficient for student projects)
- **PostgreSQL database** included
- **Automatic SSL** certificates
- **Custom domain** support

### Usage Monitoring:
- Check usage in Railway dashboard
- Monitor database storage and request volume
- Set up billing alerts if approaching limits

---

## 🆘 Quick Help Commands

### Check Deployment Status:
```bash
# If you have Railway CLI installed
railway status
railway logs
```

### Manual Commands:
```bash
# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Check deployment
railway run python manage.py check --deploy
```

---

## 📞 Support Resources

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: Community support
- **Django Deployment Guide**: [docs.djangoproject.com](https://docs.djangoproject.com/en/5.2/howto/deployment/)
- **Health Check URL**: Always test `/health/` endpoint first

---

## ✅ Success Checklist

Before submitting to professor:

- [ ] Live website accessible at Railway URL
- [ ] HTTPS certificate working (green lock icon)
- [ ] Admin interface accessible and functional
- [ ] Health check endpoint returns "healthy" status
- [ ] Database operations working (can add/view data)
- [ ] Responsive design works on mobile devices
- [ ] No 500/404 errors on main pages
- [ ] Static files (CSS/images) loading correctly

**🎉 Your CFMP application is now live and ready for evaluation!**