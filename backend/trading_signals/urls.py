# backend/trading_signals/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# Simple root view with safety measures
def root_view(request):
    try:
        return JsonResponse({
            'message': 'AlphaQuest Backend API',
            'status': 'running',
            'method': request.method,
            'endpoints': {
                'admin': '/admin/',
                'api': '/api/',
            }
        })
    except Exception as e:
        import logging
        logging.error(f"Root view error: {e}")
        return JsonResponse({'error': 'Server error', 'status': 'error'}, status=500)

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)