from .models import SiteSetting

def site_settings_processor(request):
    try:
        settings = SiteSetting.objects.first()
    except:
        settings = None
    return {'site_settings': settings}

def categories_processor(request):
    from .models import Category
    return {'categories': Category.objects.all()}
