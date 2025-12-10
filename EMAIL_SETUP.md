# Gmail SMTP Configuration Guide

## 📧 Setting Up Email Verification with Gmail

This guide will help you configure Gmail SMTP to send real verification emails from your Django application.

## Prerequisites

- A Gmail account
- 2-Step Verification enabled on your Google Account

## Step 1: Enable 2-Step Verification

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click on **2-Step Verification**
3. Follow the prompts to enable it (if not already enabled)

## Step 2: Generate App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click on **App passwords**
   - If you don't see this option, make sure 2-Step Verification is enabled
3. In the "Select app" dropdown, choose **Mail**
4. In the "Select device" dropdown, choose **Other (Custom name)**
5. Enter a name like "Django SimpleProject"
6. Click **Generate**
7. **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)
   - Remove all spaces when using it: `abcdefghijklmnop`

## Step 3: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and update the email settings:
   ```bash
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=abcdefghijklmnop
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

   Replace:
   - `your-email@gmail.com` with your actual Gmail address
   - `abcdefghijklmnop` with the 16-character App Password (no spaces)

## Step 4: Test Email Sending

1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

2. Register a new user with a real email address
3. Check your email inbox for the verification email
4. Click the verification link

## Troubleshooting

### "SMTPAuthenticationError: Username and Password not accepted"

- Make sure you're using the **App Password**, not your regular Gmail password
- Remove all spaces from the App Password
- Verify that 2-Step Verification is enabled

### "SMTPException: STARTTLS extension not supported by server"

- Make sure `EMAIL_USE_TLS=True` is set
- Verify `EMAIL_PORT=587` (not 465 or 25)

### Email not received

- Check your spam/junk folder
- Verify the email address is correct
- Check Django logs for any errors
- Make sure `DEFAULT_FROM_EMAIL` matches `EMAIL_HOST_USER`

### "Connection refused" or "Connection timed out"

- Check your internet connection
- Some networks block SMTP ports - try a different network
- Verify firewall settings

## Development vs Production

### Development (Console Backend)

For development, you can use the console backend to see emails in the terminal:

```bash
# In .env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Emails will be printed to the console where `runserver` is running.

### Production (SMTP Backend)

For production, use the SMTP backend as configured above.

## Security Notes

⚠️ **IMPORTANT**:
- Never commit your `.env` file to Git
- Keep your App Password secret
- Rotate your App Password periodically
- Use environment variables for all sensitive data

## Additional Resources

- [Django Email Documentation](https://docs.djangoproject.com/en/stable/topics/email/)
- [Google App Passwords Help](https://support.google.com/accounts/answer/185833)
- [Django Allauth Email Verification](https://django-allauth.readthedocs.io/en/latest/configuration.html)
