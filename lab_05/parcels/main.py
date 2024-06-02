from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pymongo import MongoClient
from bson import ObjectId
import requests
from typing import Optional
import jwt
import aiohttp
from pydantic import BaseModel
import redis
import json

app = FastAPI()

JWT_SECRET_KEY = 'your_secret_key'
parcels_collection = MongoClient("mongodb://mongo:mongo@mongo:27017/").get_database("arch").get_collection("parcels_collection")

class Parcel(BaseModel):
    sender_id: int
    receiver_id: int
    tracking_id: int
    delivery_id: Optional[str] = ""
    status: str
    shipment_method: Optional[str] = "unknown"

class Config:
    arbitrary_types_allowed = True

security = HTTPBasic()

redis_client = redis.Redis(host='redis', port=6379, db=0)

async def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    return credentials.username

async def get_token(username: str, password: str):
    async with aiohttp.ClientSession() as session:
        async with session.post("http://users4:8080/auth", auth=aiohttp.BasicAuth(username, password)) as response:
            print(response)
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

def cache_get(key):
    return redis_client.get(key)

def cache_set(key, value, expire=3600):
    redis_client.set(key, value, ex=expire)

@app.post("/parcels/auth/")
async def auth_parcel(username: str = Depends(get_current_username), password: str = Depends(get_current_username)):
    token = await get_token(username, password)
    return {"token": token}

@app.get("/parcels/")
async def get_parcels(token: str = Depends(verify_jwt_token)):
    cache_key = 'parcels'
    cached_parcels = cache_get(cache_key)
    if cached_parcels:
        cached_parcels = json.loads(cached_parcels.decode('utf-8'))
        return [Parcel(**parcel) for parcel in cached_parcels]
    results = list(parcels_collection.find({}, {"_id": 0}))
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
    cache_set(cache_key, json.dumps([parcel.dict() for parcel in parcels]), expire=3600)
    return parcels

@app.post("/parcels/")
async def create_parcel(parcel: Parcel, token: str = Depends(verify_jwt_token)):
    result = parcels_collection.insert_one(parcel.dict())
    return {"id": str(result.inserted_id)}

@app.get("/parcels/receiver/{receiver_id}")
async def get_parcels_by_receiver(receiver_id: int, token: str = Depends(verify_jwt_token)):
    cache_key = f'parcels:receiver:{receiver_id}'
    cached_parcels = cache_get(cache_key)
    if cached_parcels:
        cached_parcels = json.loads(cached_parcels.decode('utf-8'))
        return [Parcel(**parcel) for parcel in cached_parcels]
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
    cache_set(cache_key, json.dumps([parcel.dict() for parcel in parcels]), expire=3600)
    return parcels

@app.get("/parcels/sender/{sender_id}")
async def get_parcels_by_sender(sender_id: int, token: str = Depends(verify_jwt_token)):
    cache_key = f'parcels:sender:{sender_id}'
    cached_parcels = cache_get(cache_key)
    if cached_parcels:
        cached_parcels = json.loads(cached_parcels.decode('utf-8'))
        return [Parcel(**parcel) for parcel in cached_parcels]
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
    cache_set(cache_key, json.dumps([parcel.dict() for parcel in parcels]), expire=3600)
    return parcels