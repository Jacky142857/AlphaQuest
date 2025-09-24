# backend/trading_signals/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# Simple root view
@require_http_methods(["GET"])
def root_view(request):
    return JsonResponse({
        'message': 'AlphaQuest Backend API',
        'status': 'running',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'api_docs': '/api/docs/'
        }
    })

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)