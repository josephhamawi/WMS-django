# PythonAnywhere Deployment Guide

This guide will help you deploy your Warehouse Inventory Management System to PythonAnywhere for free.

## Prerequisites

- Your Neon PostgreSQL database URL (already configured)
- A GitHub account (to push your code)
- A PythonAnywhere account (free tier)

---

## Step 1: Push Your Code to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Prepare for PythonAnywhere deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/warehouse-inventory.git
git branch -M main
git push -u origin main
```

---

## Step 2: Create PythonAnywhere Account

1. Go to **https://www.pythonanywhere.com**
2. Click **"Pricing & signup"**
3. Choose **"Create a Beginner account"** (Free)
4. Sign up with email or GitHub

---

## Step 3: Clone Your Repository

Once logged into PythonAnywhere:

1. Click **"Consoles"** tab
2. Click **"Bash"** to start a new console
3. Run these commands:

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/warehouse-inventory.git

# Navigate to project
cd warehouse-inventory

# Create virtual environment
mkvirtualenv --python=/usr/bin/python3.10 warehouse-env

# Install dependencies
pip install -r requirements.txt
```

---

## Step 4: Configure Environment Variables

Create a `.env` file on PythonAnywhere:

```bash
cd ~/warehouse-inventory
nano .env
```

Paste this content (update with your values):

```env
# Django Settings
SECRET_KEY=your-new-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://yourusername.pythonanywhere.com

# Neon PostgreSQL Database
DATABASE_URL=postgresql://neondb_owner:npg_I9sNwLeCJBp6@ep-sparkling-wildflower-agyrgm3a-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**IMPORTANT:**
- Replace `yourusername` with your actual PythonAnywhere username
- Generate a new SECRET_KEY (you can use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)

Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

## Step 5: Run Database Migrations

Still in the Bash console:

```bash
# Make sure you're in the virtual environment
workon warehouse-env

# Navigate to project
cd ~/warehouse-inventory

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Set up user groups
python manage.py setup_groups

# Collect static files
python manage.py collectstatic --noinput
```

---

## Step 6: Configure Web App

1. Click **"Web"** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Select **"Python 3.10"**
5. Click **"Next"**

### Configure WSGI File:

1. In the Web tab, scroll to **"Code"** section
2. Click on the **WSGI configuration file** link (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
3. **Delete all content** and replace with:

```python
import os
import sys
from pathlib import Path

# Add your project directory to the sys.path
project_home = '/home/yourusername/warehouse-inventory'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env file
from dotenv import load_dotenv
project_folder = Path(project_home)
load_dotenv(project_folder / '.env')

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'warehouse_inventory.settings'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**IMPORTANT:** Replace `yourusername` with your actual PythonAnywhere username

4. Click **"Save"**

### Configure Virtual Environment:

1. Scroll to **"Virtualenv"** section
2. Enter: `/home/yourusername/.virtualenvs/warehouse-env`
3. Replace `yourusername` with your actual username

### Configure Static Files:

1. Scroll to **"Static files"** section
2. Add these mappings:

| URL          | Directory                                              |
|--------------|--------------------------------------------------------|
| /static/     | /home/yourusername/warehouse-inventory/staticfiles    |
| /media/      | /home/yourusername/warehouse-inventory/media          |

**IMPORTANT:** Replace `yourusername` with your actual PythonAnywhere username

---

## Step 7: Install Additional Dependency

PythonAnywhere needs python-dotenv to load .env files:

1. Go back to **Bash console**
2. Run:

```bash
workon warehouse-env
pip install python-dotenv
```

Add to requirements.txt:

```bash
echo "python-dotenv==1.0.0" >> requirements.txt
git add requirements.txt
git commit -m "Add python-dotenv for PythonAnywhere"
git push
```

---

## Step 8: Reload Web App

1. Go back to **"Web"** tab
2. Scroll to top
3. Click the big green **"Reload yourusername.pythonanywhere.com"** button

---

## Step 9: Access Your App

Your app should now be live at:

**https://yourusername.pythonanywhere.com**

Login with the superuser credentials you created in Step 5.

---

## Troubleshooting

### Check Error Logs:

If the site doesn't work:
1. Go to **"Web"** tab
2. Scroll to **"Log files"** section
3. Click on **"Error log"** to see what went wrong

### Common Issues:

**Issue:** ImportError or ModuleNotFoundError
- **Solution:** Make sure all packages are installed in virtual environment
- Run: `workon warehouse-env && pip install -r requirements.txt`

**Issue:** Database connection error
- **Solution:** Check your DATABASE_URL in `.env` file is correct

**Issue:** Static files not loading
- **Solution:** Run `python manage.py collectstatic` again
- Check static files paths in Web tab match your username

**Issue:** CSRF verification failed
- **Solution:** Check CSRF_TRUSTED_ORIGINS and ALLOWED_HOSTS in `.env` include your PythonAnywhere URL

---

## Updating Your App

When you make changes:

```bash
# On your local machine
git add .
git commit -m "Your changes"
git push

# On PythonAnywhere Bash console
cd ~/warehouse-inventory
git pull
workon warehouse-env
pip install -r requirements.txt  # If requirements changed
python manage.py migrate  # If models changed
python manage.py collectstatic --noinput  # If static files changed

# Then reload the web app from the Web tab
```

---

## Important Notes

- **Free tier limits:** 1 web app, always-on
- **Custom domain:** Not available on free tier (use pythonanywhere.com subdomain)
- **Database:** Uses your Neon PostgreSQL (0.5GB free)
- **Upgrade:** Can upgrade to paid plan for custom domains and more resources

---

## Your App Features

Once deployed, users can:

✅ Manage inventory (products, storage locations, units of measure)
✅ Create and approve item requests
✅ Process purchase orders and quotations
✅ Manage vendors and currencies
✅ Track item issuances
✅ Transfer items between locations
✅ Role-based access control (Requester, Staff, Supervisor, Manager)

---

## Need Help?

- PythonAnywhere forums: https://www.pythonanywhere.com/forums/
- Django docs: https://docs.djangoproject.com/
- Check error logs in PythonAnywhere Web tab

Good luck with your deployment! 🚀
