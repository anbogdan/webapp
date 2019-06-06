from django.contrib import admin
from .models import Flavor, Application

# Register your models here.

admin.site.register(Flavor)
admin.site.register(Application)