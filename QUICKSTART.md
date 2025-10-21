# Quick Start Guide

## Current Setup

Your Warehouse Inventory Management System is configured with:

✅ **Database:** PostgreSQL on Neon.tech (EU Central 1)
✅ **Framework:** Django 5.1
✅ **Ready for:** PythonAnywhere deployment

---

## Local Development

### Run the app locally:

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

### Login Credentials:

- **Username:** `admin`
- **Password:** `admin123`
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

## Database Information

**Your Neon PostgreSQL Database:**
- Region: EU Central 1
- Connection: Configured via `.env` file
- Free Tier: 0.5GB storage

**Connection String:** (stored in `.env` file)
```
DATABASE_URL=postgresql://neondb_owner:npg_I9sNwLeCJBp6@ep-sparkling-wildflower-agyrgm3a-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

---

## User Roles Available

Your app has 5 permission levels:

1. **Requester** - View inventory, create item requests
2. **Department Head** - Manage department requests
3. **Warehouse Staff** - View all transactions
4. **Warehouse Supervisor** - Add inventory, issue items
5. **Warehouse Manager** - Full permissions

Run `python manage.py setup_groups` to create these groups.

---

## Deploy to PythonAnywhere

Follow the detailed guide in **DEPLOYMENT.md**

**Quick steps:**
1. Push code to GitHub
2. Sign up at pythonanywhere.com (free)
3. Clone repo in PythonAnywhere Bash console
4. Set up virtual environment and install dependencies
5. Configure web app and WSGI file
6. Reload and go live!

**Your app will be at:** `https://yourusername.pythonanywhere.com`

---

## App Features

### Inventory Management
- Products with SKU, quantity, location tracking
- Storage locations within warehouse
- Units of measure (pieces, kg, liters, etc.)
- Low stock alerts

### Procurement
- Vendor management with contacts
- Multi-currency support
- Purchase orders with approval workflow
- Quotation requests
- Receiving process

### Requests & Issuance
- Item request creation
- Department-based requests
- Priority levels (low, medium, high, urgent)
- Approval workflow
- Item issuance tracking

### Organization
- Multiple departments
- Multiple sites/locations
- Team management
- User profiles with roles

### Transfers
- Move items between storage locations
- Track transfer history
- Approval workflow

---

## Common Commands

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Set up permission groups
python manage.py setup_groups

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver

# Access Django shell
python manage.py shell
```

---

## File Structure

```
warehouse_inventory/
├── inventory/              # Main app
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── forms.py           # Forms
│   ├── urls.py            # URL routing
│   └── migrations/        # Database migrations
├── warehouse_inventory/    # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Root URL config
│   └── templates/         # HTML templates
├── .env                    # Environment variables (not in git)
├── .env.example           # Example environment file
├── requirements.txt       # Python dependencies
├── manage.py              # Django management script
├── DEPLOYMENT.md          # Deployment guide
└── QUICKSTART.md          # This file
```

---

## Important Files

### `.env` (Keep Secret!)
Contains sensitive configuration like database URL and secret key.
**Never commit to git** - already in `.gitignore`

### `requirements.txt`
All Python packages needed:
- Django 5.1
- psycopg2-binary (PostgreSQL)
- dj-database-url (Database URL parsing)
- python-decouple (Environment variables)
- python-dotenv (For PythonAnywhere)

---

## Next Steps

1. ✅ **Test locally** - Run the app and explore features
2. ✅ **Push to GitHub** - Version control your code
3. ✅ **Deploy to PythonAnywhere** - Make it live!
4. ⬜ **Add sample data** - Populate with test products
5. ⬜ **Customize** - Adjust for your needs
6. ⬜ **Share** - Give team members access

---

## Need Help?

- **Django Documentation:** https://docs.djangoproject.com/
- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **Neon Database Docs:** https://neon.tech/docs

Happy coding! 🚀
