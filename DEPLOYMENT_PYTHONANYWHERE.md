# 🚀 Deploy Django to PythonAnywhere (Free - No Credit Card)

## Step 1: Create Account
1. Go to https://www.pythonanywhere.com
2. Click "Pricing & signup"
3. Choose "Create a Beginner account" (FREE)
4. Sign up with email

---

## Step 2: Upload Your Code

### Option A: Using Git (Recommended)
1. Open a **Bash console** from PythonAnywhere dashboard
2. Run:
```bash
git clone https://github.com/mahmoudsalemabdelrahman/SimpleProject.git
cd SimpleProject
```

### Option B: Upload Files
1. Go to "Files" tab
2. Upload your project as ZIP
3. Extract it

---

## Step 3: Create Virtual Environment

In the Bash console:
```bash
cd SimpleProject
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Step 4: Setup Database

1. Go to "Databases" tab
2. Create MySQL database
3. Note: **database name**, **username**, **password**

Update `mysite/settings.py`:
```python
# Replace DATABASES with:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'YOUR_USERNAME$dbname',
        'USER': 'YOUR_USERNAME',
        'PASSWORD': 'YOUR_PASSWORD',
        'HOST': 'YOUR_USERNAME.mysql.pythonanywhere-services.com',
    }
}
```

Install MySQL driver:
```bash
pip install mysqlclient
```

Run migrations:
```bash
cd mysite
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

---

## Step 5: Configure Web App

1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration" (NOT Django wizard)
4. Choose Python 3.10
5. Click "Next"

### Set Source Code:
- Source code: `/home/yourusername/SimpleProject/mysite`

### Set Virtual Environment:
- Virtualenv: `/home/yourusername/SimpleProject/venv`

### Configure WSGI File:
Click on WSGI file link, replace content with:
```python
import os
import sys

path = '/home/YOUR_USERNAME/SimpleProject/mysite'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Set Static Files:
Add in "Static files" section:
- URL: `/static/`
- Directory: `/home/YOUR_USERNAME/SimpleProject/mysite/staticfiles/`

Add another:
- URL: `/media/`
- Directory: `/home/YOUR_USERNAME/SimpleProject/mysite/media/`

---

## Step 6: Update Settings

Edit `mysite/settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['YOUR_USERNAME.pythonanywhere.com']

# Add at the end:
CSRF_TRUSTED_ORIGINS = ['https://YOUR_USERNAME.pythonanywhere.com']
```

---

## Step 7: Reload and Test

1. Click green "Reload" button
2. Visit: `https://YOUR_USERNAME.pythonanywhere.com`

---

## ✅ Done! Your Site is Live!

**Admin Panel:** `https://YOUR_USERNAME.pythonanywhere.com/secure-admin/`

---

## 🔄 Update Your Site

When you make changes:
```bash
# In PythonAnywhere Bash console:
cd SimpleProject
git pull
source venv/bin/activate
cd mysite
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
# Then reload web app from Web tab
```

---

## 📝 Important Notes

1. **Free account limits:**
   - Always-on: Yes ✅
   - Bandwidth: 100K hits/day
   - Storage: 512 MB

2. **Renewal:** Click "Run until" button every 3 months (free)

3. **Logs:** Check error logs in "Web" tab if issues occur

4. **Console:** Use Bash console to run Django commands

---

## 🐛 Troubleshooting

### Site shows error:
- Check error log in Web tab
- Verify WSGI file paths
- Check ALLOWED_HOSTS in settings.py

### Static files don't load:
- Run `python manage.py collectstatic`
- Check static files mapping in Web tab

### Database error:
- Verify database credentials
- Check if mysqlclient is installed
- Ensure migrations are run

---

**Support:** https://help.pythonanywhere.com
