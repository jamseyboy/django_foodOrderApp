from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from datetime import date
from django.utils import timezone
from collections import defaultdict
from .schemas import updateOrderStatusSchema,FoodInfoSchema, CustomerOrderSchema, customerInfoSchema, orderItemSchema, createOrdersSchema, createCustomer, createOrderItem
from .models import customerModel, orderItemModel, orderModel
from food.models import foodModel




router = Router()



@router.get("food_info_all", response = List[FoodInfoSchema])
def customers_order_list(request):
    qs= foodModel.objects.all()
    return qs



@router.get("customer_info_all", response = List[customerInfoSchema])
def customers_order_list(request):
    qs= customerModel.objects.all()
    return qs




@router.post("create_customer")
def create_customer(request, payload:createCustomer):
    qs=customerModel.objects.create(**payload.dict())
    return {"user_id": qs.id, "username":qs.username}



@router.get("orderslist") #to retrieve all orders list
def get_orders_list(request):
    qs=orderModel.objects.all()
    data_list=[]
    for order_value in qs:
        db_value={
            "id":order_value.id,
            "customer_id": order_value.customer_info.id,
            "username":order_value.customer_info.username,
            "order_status":order_value.order_status,
            "timestamp":order_value.timestamp,
        }
        data_list.append(db_value)

    return {"order":data_list}




@router.post("create_orders")
def create_customer_orders(request, payload:createOrdersSchema):
    print(payload.dict())
    customer_info_from_db=get_object_or_404(customerModel, id = payload.customer_id)
    customer_order_data =orderModel.objects.create(
            order_status=payload.order_status,
            customer_info=customer_info_from_db
            )
    print(customer_order_data)
    return {"order_id":customer_order_data.id}


@router.post("create_order_item")
def create_order_item(request, payload:createOrderItem):
    order_info_from_db=get_object_or_404(orderModel, id = payload.order_id)
    order_info_from_db.order_status=payload.order_status
    order_info_from_db.save()
    food_info_from_db=get_object_or_404(foodModel, id=payload.food_id)
    order_item_data=orderItemModel.objects.create(
        order_info=order_info_from_db,
        food_info = food_info_from_db,
        food_quantity  =payload.food_quantity,
        total_amount = food_info_from_db.food_price * payload.food_quantity
    )
    return {"order_item_id": order_item_data.id}

@router.post("update_order_status")
def update_order_status(request, payload:updateOrderStatusSchema):
    get_order_status_by_id=get_object_or_404(orderModel, id=payload.id)
    get_order_status_by_id.order_status=payload.order_status
    get_order_status_by_id.save()
    return {"Success" : 1}

@router.get("todays_detail_order_list")
def get_todays_detail_order_list(request):

    #qs=orderItemModel.objects.filter(timestamp__gte = date.today()) #.select_related('order_info').order_by('order_info__customer_info__username')
    qs=orderItemModel.objects.all()
    order_details_by_customer= defaultdict(list)

    order_detailsItem=[]
    for item_details in qs:
        db_value={
            "id" : item_details.id,
            "order_id": item_details.order_info.id,
            #"customer_id":item_details.order_info.customer_info.id,
            #"customer_name":item_details.order_info.customer_info.username,
            "order_status":item_details.order_info.order_status,
            #"food_id":item_details.food_info.id,
            "food_name":item_details.food_info.food_name,
            "food_price":item_details.food_info.food_price,
            "food_quantity":item_details.food_quantity,
            "total_amount":item_details.total_amount,
            "timestamp": item_details.timestamp,
        }

        # db_value={

        #     "order_info":list(item_details.order_info),
        #     "food_info":list(item_details.food_info),
        #     "customer_info":list(item_details.order_info.customer_info),
        #     "food_quantity":item_details.food_quantity,
        #     "total_amount":item_details.total_amount

        #     }
        customer_name = item_details.order_info.customer_info.username
        order_details_by_customer[customer_name].append(db_value)
    order_details_by_customer = dict(order_details_by_customer)
    #order_detailsItem.sort(key=lambda x:x['customer_name'])
    #sorted_return_value=sorted(order_details_by_customer, key=lambda x:x['customer_name'])
    return {"todayOrderDetails": order_details_by_customer}

