## 🧩 SimpleProject - Django LMS & Blog

مشروع Django متكامل يحتوي على:
- نظام مقالات (Blog) مع تصنيفات ووسوم وتعليقات
- كورسات (Courses) ودروس (Lessons) وتتبّع تقدّم المستخدم
- اختبارات (Quizzes) وشهادات (Certificates) توليد PDF
- نظام تسجيل/دخول باستخدام `django-allauth`
- مدفوعات باستخدام Stripe

### 🔧 المتطلبات (Requirements)

استخدم ملف `requirements.txt` الموجود في جذر المشروع:

```bash
pip install -r requirements.txt
```

أهم الحزم:
- Django 5.2+
- django-allauth
- django-autoslug
- django-extensions
- Pillow
- stripe
- python-decouple
- whitenoise
- mysqlclient (للإنتاج مع MySQL)
- reportlab و qrcode لتوليد الشهادات

### ⚙️ إعداد المتغيرات السرية (Environment Variables)

الملف `mysite/mysite/settings.py` يستخدم `decouple.config` و/أو `os.environ`، لذا على بيئة التشغيل أن تحتوي على:

- `SECRET_KEY`
- `DEBUG` (`True` أو `False`)
- `ALLOWED_HOSTS` (قائمة مفصولة بفواصل)
- `DATABASE_URL` (في حالة استخدام PostgreSQL أو MySQL على الاستضافة)
- `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- `SITE_URL`

### ▶️ تشغيل المشروع محلياً

```bash
cd g:/Django/SimpleProject
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd mysite
python manage.py migrate
python manage.py runserver
```

ثم افتح: `http://127.0.0.1:8000/`

### 🚀 رفع المشروع إلى GitHub

من جذر المشروع `g:/Django/SimpleProject`:

```bash
git init
git add .
git commit -m "Initial commit: Django LMS & Blog project"

git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

> **ملاحظة:** غيّر `YOUR_USERNAME` و `YOUR_REPO` إلى بيانات حسابك في GitHub.

### 🌐 دليل النشر (Deployment)

- نشر على Render: انظر ملف `DEPLOYMENT.md`
- نشر على PythonAnywhere: انظر ملف `DEPLOYMENT_PYTHONANYWHERE.md`

### 🧪 الاختبارات

من داخل مجلد `mysite`:

```bash
python manage.py test
```

ملف `test_output.txt` يحتوي على نتائج سابقة للاختبارات للمراجعة.

### ✅ التعديلات الأخيرة (تمّت محلياً)

- أصلحت خطأ استيراد في اختبارات `blog` (`mysite/blog/tests/test_general.py`) بحيث تستخدم الآن الاستيراد النسبي الصحيح.
- حدّثت إعدادات `django-allauth` إلى الصيغة الموصى بها: استخدمت `ACCOUNT_LOGIN_METHODS` و `ACCOUNT_SIGNUP_FIELDS` بدلاً من الإعدادات المتهالكة.
- أنشأت مجلد `mysite/staticfiles` لمعايرة `STATIC_ROOT` وإزالة تحذيرات الاختبارات المتعلقة بغياب المجلد.

بعد هذه التعديلات شغّلت اختبارات التطبيقات الأساسية (`blog`, `payments`) محلياً وتجاوزت بنجاح (31 tests, OK).

إذا رغبت، أستطيع:
- تشغيل كامل الاختبارات مرة أخرى.
- فتح فرع خاص ورفع Pull Request للتغييرات بدلاً من الدمج المباشر على `main`.



