# backend/api/urls.py
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from . import views, auth_views

# API root view
@require_http_methods(["GET"])
def api_root(request):
    return JsonResponse({
        'message': 'AlphaQuest API v1.0',
        'endpoints': {
            'data': {
                'load_dow30': '/api/load-dow30/ (POST)',
                'upload_data': '/api/upload-data/ (POST)',
                'upload_multiple': '/api/upload-multiple-data/ (POST)',
                'calculate_alpha': '/api/calculate-alpha/ (POST)',
            },
            'auth': {
                'register': '/api/auth/register/ (POST)',
                'login': '/api/auth/login/ (POST)',
                'user': '/api/auth/user/ (GET)',
            }
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    # Data management endpoints
    path('upload-data/', views.upload_data, name='upload_data'),
    path('upload-multiple-data/', views.upload_multiple_data, name='upload_multiple_data'),
    path('load-dow30/', views.load_dow30_data, name='load_dow30_data'),
    path('load-yfinance/', views.load_yfinance_data_view, name='load_yfinance_data'),
    path('set-date-range/', views.set_date_range, name='set_date_range'),
    path('calculate-alpha/', views.calculate_alpha, name='calculate_alpha'),
    path('update-settings/', views.update_settings_view, name='update_settings'),
    path('get-settings/', views.get_settings_view, name='get_settings'),

    # Authentication endpoints
    path('auth/register/', auth_views.register_user, name='register_user'),
    path('auth/login/', auth_views.login_user, name='login_user'),
    path('auth/logout/', auth_views.logout_user, name='logout_user'),
    path('auth/user/', auth_views.get_current_user, name='get_current_user'),

    # Alpha management endpoints
    path('alphas/save/', auth_views.save_alpha, name='save_alpha'),
    path('alphas/<str:alpha_id>/delete/', auth_views.delete_alpha, name='delete_alpha'),
    path('alphas/<str:alpha_id>/update/', auth_views.update_alpha, name='update_alpha'),
]