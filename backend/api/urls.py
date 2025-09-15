# backend/api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload-data/', views.upload_data, name='upload_data'),
    path('load-dow30/', views.load_dow30_data, name='load_dow30_data'),
    path('set-date-range/', views.set_date_range, name='set_date_range'),
    path('calculate-alpha/', views.calculate_alpha, name='calculate_alpha'),
    path('update-settings/', views.update_settings, name='update_settings'),
    path('get-settings/', views.get_settings, name='get_settings'),
]