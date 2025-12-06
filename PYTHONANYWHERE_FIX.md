# PythonAnywhere Deployment - Fix Instructions

## خطوات إصلاح الأخطاء على PythonAnywhere

### 1. تحديث الكود من GitHub
```bash
cd ~/SimpleProject
git pull origin main
```

### 2. تفعيل البيئة الافتراضية
```bash
source ~/SimpleProject/venv/bin/activate
```

### 3. تثبيت المكتبات الجديدة
```bash
pip install django-ckeditor-5
pip install xhtml2pdf
```

أو تثبيت كل المكتبات من requirements.txt:
```bash
cd ~/SimpleProject/mysite
pip install -r requirements.txt
```

### 4. تطبيق Migrations الجديدة
```bash
cd ~/SimpleProject/mysite
python manage.py migrate
```

### 5. جمع الملفات الثابتة
```bash
python manage.py collectstatic --noinput
```

### 6. إعادة تحميل التطبيق
- اذهب إلى **Web** tab في PythonAnywhere
- اضغط على زر **Reload** الأخضر الكبير

---

## التحقق من نجاح التثبيت

بعد إعادة التحميل، جرب:
1. زيارة الصفحة الرئيسية
2. الدخول إلى Admin Panel
3. تحقق من عمل الإشعارات
4. تأكد من ظهور محرر النصوص في Admin

---

## المكتبات الجديدة المضافة:
- ✅ `django-ckeditor-5` - محرر النصوص الغني
- ✅ `xhtml2pdf` - لتوليد شهادات PDF بصيغة HTML

## الإصلاحات:
- ✅ إصلاح خطأ `notifications_list` view (TypeError)
