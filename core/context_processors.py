from django.conf import settings

def settings_context(request):
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'EMPLOYEE_MEDIA_URL': settings.EMPLOYEE_MEDIA_URL
    }