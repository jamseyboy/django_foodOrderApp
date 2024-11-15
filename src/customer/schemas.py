from datetime import datetime
from ninja import Schema
from typing import List, Dict, Any
from pydantic import BaseModel




class FoodInfoSchema(Schema):
    id: int
    food_name:str
    food_price:int
    
class customerInfoSchema(Schema):
    id: int
    username:str

class createCustomer(Schema):
    username:str
class updateOrderStatusSchema(Schema):
    id:int
    order_status:str

class CustomerOrderSchema(Schema):
    #create -> Data
    id: int
    customer_info:List[customerInfoSchema]
    order_status:str
    timestamp:datetime

class createOrdersSchema(Schema):
    customer_id:int
    order_status:str

class orderItemSchema(Schema):

    id:int
    food_quantity:int
    total_amount:int
    order_info:List[CustomerOrderSchema]
    food_info:List[FoodInfoSchema]
   
    class Config:
        orm_mode=True

class foodSchema(Schema):
    food_id:int
    food_quantity:int


class createOrderItem(Schema):

    order_id:int
    order_status:str
    items:List[foodSchema]
    class Config:
        extra = "allow"  # Allows additional fields in the root schema as well

