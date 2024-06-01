from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

app = FastAPI()

def get_current_date():
    return datetime.now().date()

deliveries_collection = MongoClient(
    f"mongodb://mongo:mongo@mongo:27017/").get_database("arch").get_collection("deliveries_collection")


class Delivery(BaseModel):
    sender_id: int
    receiver_id: int
    status: str
    date: datetime = Field(default_factory=get_current_date)

    class Config:
        arbitrary_types_allowed = True

@app.post("/deliveries/")
def create_delivery(delivery: Delivery):
    result = deliveries_collection.insert_one(delivery.dict())
    return {"id": str(result.inserted_id)}

@app.get("/deliveries/{delivery_id}")
def get_delivery(delivery_id: str):
    result = deliveries_collection.find_one({"_id": ObjectId(delivery_id)})
    if result:
        return Delivery(**result)
    else:
        raise HTTPException(status_code=404, detail="Delivery not found")

@app.get("/deliveries/")
def get_all_deliveries():
    results = list(deliveries_collection.find({}, {"_id": 0}))
    deliveries = []
    for result in results:
        delivery = {
            "sender_id": result.get("sender_id"),
            "receiver_id": result.get("receiver_id"),
            "tracking_id": result.get("tracking_id", 0),  
            "delivery_id": result.get("delivery_id", ""),
            "status": result.get("status"),
            "date": get_current_date() if result.get("date") is None else result.get("date")
        }
        deliveries.append(Delivery(**delivery))
    return deliveries

@app.get("/deliveries/user/{user_id}")
def get_user_deliveries(user_id: int):
    results = list(deliveries_collection.find({"sender_id": user_id}, {"_id": 0}))
    deliveries = []
    for result in results:
        delivery = {
            "sender_id": result.get("sender_id"),
            "receiver_id": result.get("receiver_id"),
            "tracking_id": result.get("tracking_id", 0),  
            "delivery_id": result.get("delivery_id", ""),
            "status": result.get("status"),
            "date": get_current_date() if result.get("date") is None else result.get("date")
        }
        deliveries.append(Delivery(**delivery))
    return deliveries

@app.post("/deliveries/user/{user_id}")
def create_user_delivery(user_id: int, delivery: Delivery):
    delivery.sender_id = user_id
    result = deliveries_collection.insert_one(delivery.dict())
    return {"id": str(result.inserted_id)}