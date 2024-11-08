from django.db import models
from food.models import foodModel
# Create your models here.

class customerModel(models.Model):

    username=models.CharField(max_length=100)
    def __str__(self):
        return self.username
    

class orderModel(models.Model):

    customer_info=models.ForeignKey(customerModel, related_name="orders", on_delete=models.CASCADE)
    order_status=models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now=True)

class orderItemModel(models.Model):
    order_info=models.ForeignKey(orderModel, related_name="items", on_delete=models.CASCADE)
    food_info=models.ForeignKey(foodModel, related_name="food", on_delete=models.CASCADE)
    food_quantity=models.IntegerField()
    total_amount=models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)


