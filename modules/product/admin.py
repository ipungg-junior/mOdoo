from django.contrib import admin
from .models import ChoosenDatabase, ChoosenDatabaseConfig

# Register your models here.
admin.site.register(ChoosenDatabase)
admin.site.register(ChoosenDatabaseConfig)