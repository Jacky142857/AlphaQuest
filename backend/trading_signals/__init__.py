# backend/trading_signals/__init__.py
# Empty file

# backend/api/__init__.py  
# Empty file

# backend/api/apps.py
from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

# backend/api/admin.py
from django.contrib import admin
# Register your models here.

# backend/api/models.py
from django.db import models
# Create your models here.

# backend/api/tests.py
from django.test import TestCase
# Create your tests here.