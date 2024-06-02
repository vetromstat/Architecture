from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pymongo import MongoClient
from bson import ObjectId
import jwt
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import aiohttp

app = FastAPI()

JWT_SECRET_KEY = 'your_secret_key'

deliveries_collection = MongoClient("mongodb://mongo:mongo@mongo:27017/").get_database("arch").get_collection("deliveries_collection")

class Delivery(BaseModel):
    sender_id: int
    receiver_id: int
    status: str
    date: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True

security = HTTPBasic()

async def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    return credentials.username

async def get_token(username: str, password: str):
    async with aiohttp.ClientSession() as session:
        async with session.post("http://users3:8080/auth", auth=aiohttp.BasicAuth(username, password)) as response:
            if response.status == 200:
                token = await response.json()
                return token
            else:
                raise HTTPException(status_code=401, detail="Incorrect username or password")

async def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

@app.post("/deliveries/auth/")
async def auth_delivery(username: str = Depends(get_current_username), password: str = Depends(get_current_username)):
    token = await get_token(username, password)
    return {"token": token}

@app.post("/deliveries/")
async def create_delivery(delivery: Delivery, token: str = Depends(verify_jwt_token)):
    result = deliveries_collection.insert_one(delivery.dict())
    return {"id": str(result.inserted_id)}

@app.get("/deliveries/{delivery_id}")
async def get_delivery(delivery_id: str, token: str = Depends(verify_jwt_token)):
    result = deliveries_collection.find_one({"_id": ObjectId(delivery_id)})
    if result:
        return Delivery(**result)
    else:
        raise HTTPException(status_code=404, detail="Delivery not found")

@app.get("/deliveries/")
async def get_all_deliveries(token: str = Depends(verify_jwt_token)):
    results = list(deliveries_collection.find({}, {"_id": 0}))
    deliveries = []
    for result in results:
        delivery = {
            "sender_id": result.get("sender_id"),
            "receiver_id": result.get("receiver_id"),
            "tracking_id": result.get("tracking_id", 0),  
            "delivery_id": result.get("delivery_id", ""),
            "status": result.get("status"),
            "date": result.get("date")
        }
        deliveries.append(Delivery(**delivery))
    return deliveries

@app.get("/deliveries/user/{user_id}")
async def get_user_deliveries(user_id: int, token: str = Depends(verify_jwt_token)):
    results = list(deliveries_collection.find({"sender_id": user_id}, {"_id": 0}))
    deliveries = []
    for result in results:
        delivery = {
            "sender_id": result.get("sender_id"),
            "receiver_id": result.get("receiver_id"),
            "tracking_id": result.get("tracking_id", 0),  
            "delivery_id": result.get("delivery_id", ""),
            "status": result.get("status"),
            "date": result.get("date")
        }
        deliveries.append(Delivery(**delivery))
    return deliveries

@app.post("/deliveries/user/{user_id}")
async def create_user_delivery(user_id: int, delivery: Delivery, token: str = Depends(verify_jwt_token)):
    delivery.sender_id = user_id
    result = deliveries_collection.insert_one(delivery.dict())
    return {"id": str(result.inserted_id)}