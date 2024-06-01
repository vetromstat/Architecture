from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()
parcels_collection = MongoClient(
    f"mongodb://mongo:mongo@mongo:27017/").get_database("arch").get_collection("parcels_collection")


class Parcel(BaseModel):
    sender_id: int
    receiver_id: int
    tracking_id: int
    delivery_id: Optional[str] = ""
    status: str
    shipment_method: Optional[str] = "unknown"
    
    class Config:
        arbitrary_types_allowed = True

@app.get("/parcels/")
async def get_parcels():
    results = list(parcels_collection.find({}, {"_id": 0}))
    parcels = []
    print(results)
    for result in results:
        parcel = {
            "sender_id": result.get("sender_id"),
            "receiver_id": result.get("receiver_id"),
            "tracking_id": result.get("tracking_id"),
            "status": result.get("status"),
            "shipment_method": result.get("shipment_method")
        }
        parcels.append(Parcel(**parcel))
    return parcels

@app.post("/parcels/")
async def create_parcel(parcel: Parcel):
    result = parcels_collection.insert_one(parcel.dict())
    return {"id": str(result.inserted_id)}

@app.get("/parcels/receiver/{receiver_id}")
async def get_parcels_by_receiver(receiver_id: int):
    results = list(parcels_collection.find({"receiver_id": receiver_id}, {"_id": 0}))
    parcels = []
    for result in results:
        parcel = {
            "sender_id": result.get("sender_id"),
            "receiver_id": result.get("receiver_id"),
            "tracking_id": result.get("tracking_id"),
            "status": result.get("status"),
            "shipment_method": result.get("shipment_method")
        }
        parcels.append(Parcel(**parcel))
    return parcels

@app.get("/parcels/sender/{sender_id}")
async def get_parcels_by_sender(sender_id: int):
    results = list(parcels_collection.find({"sender_id": sender_id}, {"_id": 0}))
    parcels = []
    for result in results:
        parcel = {
            "sender_id": result.get("sender_id"),
            "receiver_id": result.get("receiver_id"),
            "tracking_id": result.get("tracking_id"),
            "status": result.get("status"),
            "shipment_method": result.get("shipment_method")
        }
        parcels.append(Parcel(**parcel))
    return parcels