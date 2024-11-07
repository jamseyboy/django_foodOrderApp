from django.contrib import admin

# Register your models here.

from .models import orderItemModel, orderModel, customerModel

admin.site.register(orderItemModel)
admin.site.register(orderModel)
admin.site.register(customerModel)
