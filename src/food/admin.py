from django.contrib import admin

# Register your models here.

from .models import foodModel

admin.site.register(foodModel)
