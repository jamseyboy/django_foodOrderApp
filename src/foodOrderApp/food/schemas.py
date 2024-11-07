from datetime import datetime
from ninja import Schema
from typing import List




class FoodInfoSchema(Schema):
    id: int
    food_name:str
    food_price:int
    timestamp:datetime

class createFood(Schema):

    food_name:str
    food_price:int
