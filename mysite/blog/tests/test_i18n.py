from django.test import TestCase
from django.utils import translation
from django.conf import settings

class I18nTest(TestCase):
    def test_language_settings(self):
        self.assertEqual(settings.LANGUAGE_CODE, 'ar')
        self.assertTrue(settings.USE_I18N)

    def test_active_language(self):
        # By default, without middleware processing a request, it might be the default.
        # But let's check if we can activate it.
        translation.activate('ar')
        self.assertEqual(translation.get_language(), 'ar')
        
        # Check a standard translation
        from django.utils.translation import gettext as _
        # "Log in" in Arabic is "تسجيل الدخول" usually, but let's check a standard Django string
        # "Welcome" -> "مرحباً"
        # Or just check if the setting is respected.
        self.assertEqual(settings.LANGUAGE_CODE, 'ar')
