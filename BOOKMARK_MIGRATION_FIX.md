# حل مشكلة Bookmark Migration Error

## المشكلة
إذا واجهت الخطأ التالي:
```
django.db.utils.IntegrityError: NOT NULL constraint failed: new__blog_bookmark.content_type_id
```

## الحل السريع

### الطريقة 1: حذف قاعدة البيانات وإعادة إنشائها (للتطوير فقط)
```bash
# احذف ملف قاعدة البيانات
rm db.sqlite3

# أعد إنشاء القاعدة وطبق جميع الـ migrations
python manage.py migrate

# أنشئ superuser جديد
python manage.py createsuperuser
```

### الطريقة 2: حذف الـ bookmarks القديمة فقط
افتح Python shell:
```bash
python manage.py shell
```

ثم نفذ:
```python
from blog.models import Bookmark
Bookmark.objects.all().delete()
exit()
```

ثم طبق الـ migrations:
```bash
python manage.py migrate
```

### الطريقة 3: للـ Production (على PythonAnywhere)
قبل عمل `git pull` و `migrate`، افتح console ونفذ:

```bash
cd ~/SimpleProject/mysite
source ~/SimpleProject/venv/bin/activate
python manage.py shell
```

ثم:
```python
from blog.models import Bookmark
Bookmark.objects.all().delete()
exit()
```

ثم:
```bash
git pull origin main
python manage.py migrate
python manage.py collectstatic --noinput
```

ثم Reload Web App.

---

## ملاحظة مهمة
هذا الخطأ يحدث مرة واحدة فقط عند التحديث من النظام القديم للـ bookmarks إلى النظام الجديد (ContentTypes).
بعد حل المشكلة لن تظهر مرة أخرى.
