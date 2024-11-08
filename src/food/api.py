from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from datetime import date
from django.utils import timezone
from .schemas import FoodInfoSchema, createFood
from .models import foodModel




router = Router()

@router.get("food_info_all")
def customers_order_list(request):
    qs= foodModel.objects.all()
    return list(qs.values())


@router.post("create_food")
def create_food(request, payload:createFood):
    qs=foodModel.objects.create(**payload.dict())

    return {"Food_id":qs.id}

@router.get("todays_food")
def get_todays_food(request):
    qs= foodModel.objects.filter(timestamp__gte = timezone.now().today())
    return list(qs.values())