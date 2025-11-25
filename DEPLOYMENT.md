# 🚀 Deployment Guide - Render.com

This guide will help you deploy your Django project to Render.com for free.

## Prerequisites
- GitHub account
- Render.com account (sign up at https://render.com)

## Step 1: Push Your Code to GitHub

1. Initialize Git repository (if not done):
```bash
cd g:/Django/SimpleProject
git init
git add .
git commit -m "Prepare for deployment"
```

2. Create a new repository on GitHub

3. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

## Step 2: Create PostgreSQL Database on Render

1. Go to https://dashboard.render.com
2. Click "New +" → "PostgreSQL"
3. Fill in:
   - **Name**: `mysite-db`
   - **Database**: `mysite`
   - **User**: `mysite_user`
   - **Region**: Choose nearest
   - **Plan**: Free
4. Click "Create Database"
5. **Save the Internal Database URL** (you'll need it)

## Step 3: Create Web Service on Render

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Fill in:
   - **Name**: `mysite` (or your preferred name)
   - **Region**: Choose nearest
   - **Branch**: `main`
   - **Root Directory**: `mysite`
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn mysite.wsgi:application`
   - **Plan**: Free

## Step 4: Add Environment Variables

In the web service settings, add these environment variables:

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=<paste-your-postgres-internal-url>
STRIPE_PUBLIC_KEY=pk_test_YOUR_KEY
STRIPE_SECRET_KEY=sk_test_YOUR_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
SITE_URL=https://mysite.onrender.com
```

**To generate a SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 5: Deploy!

1. Click "Create Web Service"
2. Render will automatically:
   - Install dependencies from `requirements.txt`
   - Run `build.sh` (collectstatic + migrate)
   - Start your app with gunicorn

## Step 6: Access Your Site

Your site will be available at: `https://mysite.onrender.com`

**Note:** The free tier:
- Spins down after 15 minutes of inactivity
- Takes ~30 seconds to wake up on first request
- 750 hours/month free (enough for one always online)

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure `build.sh` has execute permissions: `chmod +x build.sh`

### Static Files Don't Load
- Verify `STATIC_ROOT` in settings.py
- Check `whitenoise` is in `INSTALLED_APPS`
- Ensure build command runs `collectstatic`

### Database Connection Error
- Verify `DATABASE_URL` environment variable
- Check PostgreSQL service is running

## Optional: Custom Domain

1. Add your domain in Render dashboard
2. Update DNS records as instructed
3. Update `ALLOWED_HOSTS` to include your domain

## Monitoring

- Check logs: Click "Logs" in Render dashboard
- View metrics: Click "Metrics" tab
- Set up alerts: Click "Notifications"

---

**Your Django app is now live! 🎉**
