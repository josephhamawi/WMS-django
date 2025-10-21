# Render.com Deployment Guide

Deploy your Warehouse Inventory Management System to Render.com with PostgreSQL support.

## Why Render?

✅ Free tier with external database support
✅ Works with your Neon PostgreSQL database
✅ Auto-deploys from GitHub
✅ HTTPS included
✅ Easier than PythonAnywhere for Django

**Note:** Free tier sleeps after 15 minutes of inactivity (wakes up instantly when visited)

---

## Prerequisites

- ✅ Code pushed to GitHub
- ✅ Neon PostgreSQL database (already set up)

---

## Step-by-Step Deployment

### 1. Create Render Account

1. Go to **https://render.com**
2. Click **"Get Started"**
3. Sign up with **GitHub** (easiest option)
4. Authorize Render to access your repositories

---

### 2. Create New Web Service

1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Connect your **GitHub repository**: `josephhamawi/WMS-django`
4. Click **"Connect"**

---

### 3. Configure Web Service

Fill in these settings:

**Basic Settings:**
- **Name:** `warehouse-inventory` (or any name you prefer)
- **Region:** Choose closest to you (e.g., Frankfurt for EU, Oregon for US)
- **Branch:** `main`
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn warehouse_inventory.wsgi:application`

**Instance Type:**
- Select **"Free"** (should be pre-selected)

---

### 4. Add Environment Variables

Scroll down to **"Environment Variables"** section and click **"Add Environment Variable"**

Add these variables one by one:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Generate new key (see below) |
| `DEBUG` | `False` |
| `DATABASE_URL` | `postgresql://neondb_owner:npg_I9sNwLeCJBp6@ep-sparkling-wildflower-agyrgm3a-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require` |
| `PYTHON_VERSION` | `3.10.0` |

**To generate a SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Note:** ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS will be automatically set by Render based on your app URL.

---

### 5. Deploy!

1. Click **"Create Web Service"** at the bottom
2. Render will start building your app (takes 3-5 minutes)
3. Watch the build logs for any errors

**Expected flow:**
- Installing dependencies
- Collecting static files
- Running migrations
- Setting up user groups
- Starting Gunicorn server

---

### 6. Update Django Settings for Render

After deployment, you need to update ALLOWED_HOSTS:

1. Your app URL will be: `https://warehouse-inventory.onrender.com` (or your chosen name)
2. Add two more environment variables in Render dashboard:

| Key | Value |
|-----|-------|
| `ALLOWED_HOSTS` | `warehouse-inventory.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://warehouse-inventory.onrender.com` |

Replace `warehouse-inventory` with your actual service name.

3. Click **"Manual Deploy"** → **"Deploy latest commit"** to apply changes

---

### 7. Create Admin User

Once deployed, you need to create an admin account:

1. Go to Render dashboard → Your service
2. Click **"Shell"** tab on the left
3. Wait for shell to connect
4. Run:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

---

### 8. Access Your App

Your app will be available at:

**https://warehouse-inventory.onrender.com**

(Replace with your actual service name)

**Admin panel:**
**https://warehouse-inventory.onrender.com/admin/**

---

## Important Notes

### Free Tier Limitations

- ✅ Always-on database (Neon)
- ⚠️ Web service sleeps after 15 min inactivity
- ⚠️ Takes ~30 seconds to wake up on first request
- ✅ 750 hours/month free (enough for most use cases)

### Keeping Service Awake (Optional)

Use a free uptime monitoring service to ping your app:
- UptimeRobot: https://uptimerobot.com
- Cron-job.org: https://cron-job.org

Set it to ping your URL every 14 minutes to prevent sleeping.

---

## Updating Your App

When you make changes:

```bash
# On your local machine
git add .
git commit -m "Your changes"
git push origin main
```

Render will **automatically deploy** the new version!

Or manually deploy from Render dashboard:
- Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## Troubleshooting

### Check Logs

In Render dashboard → Your service → **"Logs"** tab

### Common Issues

**Build fails:**
- Check build.sh has correct permissions (`chmod +x build.sh`)
- Verify requirements.txt has all dependencies

**App won't start:**
- Check environment variables are set correctly
- Verify DATABASE_URL is correct
- Check logs for specific errors

**Static files not loading:**
- Verify WhiteNoise is in MIDDLEWARE
- Check STATIC_ROOT is set in settings.py

**Database connection error:**
- Verify DATABASE_URL is correct (no line breaks!)
- Check Neon database is active

---

## Your App Features

Once deployed, your warehouse inventory system includes:

✅ Product management with SKU tracking
✅ Storage location management
✅ Vendor and procurement management
✅ Purchase orders and quotations
✅ Item request and approval workflow
✅ Item issuance tracking
✅ Transfer management between locations
✅ Role-based access control
✅ Multi-currency support

---

## Support

- Render Docs: https://render.com/docs
- Django Docs: https://docs.djangoproject.com/
- Neon Docs: https://neon.tech/docs

---

Good luck with your deployment! 🚀
