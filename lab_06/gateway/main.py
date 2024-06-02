from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from typing import Optional
import jwt
import aiohttp
import redis
import json
from datetime import datetime

app = FastAPI()

JWT_SECRET_KEY = 'your_secret_key'

redis_client = redis.Redis(host='redis', port=6379, db=0)

security = HTTPBasic()

async def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    return credentials.username

async def get_token(username: str, password: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://users5:8080/auth", auth=aiohttp.BasicAuth(username, password)
        ) as response:
            if response.status == 200:
                token = await response.json()
                return token["access_token"]
            else:
                raise HTTPException(
                    status_code=401, detail="Incorrect username or password"
                )

async def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def cache_get(key):
    return redis_client.get(key)

def cache_set(key, value, expire=3600):
    redis_client.set(key, value, ex=expire)

def serialize_datetime(obj): 
    if isinstance(obj, datetime): 
        return obj.isoformat() 
    raise TypeError("Type not serializable") 

class Parcel(BaseModel):
    sender_id: int
    receiver_id: int
    delivery_id: Optional[str] = ""
    status: str
    shipment_method: Optional[str] = "unknown"

class Delivery(BaseModel):
    sender_id: int
    receiver_id: int
    status: str
    date: datetime = Field(default_factory=datetime.now)

@app.post("/auth", response_model=str)
async def auth_api(username: str = Depends(get_current_username), password: str = Depends(get_current_username)):
    token = await get_token(username, password)
    return token

@app.post("/parcels", response_model=Parcel)
async def create_parcel(parcel: Parcel, token: str = Depends(verify_jwt_token)):
    print("Received parcel request:", parcel)
    print("Token:", token)
    print("dict:",  parcel.dict())
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("http://parcels5:8080/parcels", data=parcel.dict()) as response:
                print("Response:", response)
                if response.status == 200:
                    parcel_response_text = await response.text()
                    print(parcel_response_text)
                    parcel_response = json.loads(parcel_response_text)
                    return Parcel(delivery_id=parcel_response["delivery_id"], sender_id=parcel_response["sender_id"], status=parcel_response["status"], shipment_method=parcel_response["shipment_method"], receiver_id=parcel_response["receiver_id"])
                else:
                    print(response.text())
                    raise HTTPException(status_code=response.status, detail="Parcel creation failed")
    except HTTPException as e:
        raise e
    except Exception as e:
        print("Error creating parcel:", e)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/deliveries", response_model=Delivery)
async def create_delivery(delivery: Delivery, token: str = Depends(verify_jwt_token)):
    async with aiohttp.ClientSession() as session:
        async with session.post("http://deliveries5:8080/deliveries", data=delivery.dict()) as response:
            if response.status == 200:
                delivery_response = await response.json()
                return Delivery(sender_id=delivery_response["sender_id"], status=delivery_response["status"], receiver_id=delivery_response["receiver_id"], date= delivery_response["date"])
            else:
                raise HTTPException(status_code=response.status, detail="Delivery creation failed")

@app.get("/parcels/{tracking_id}")
async def get_parcel_by_tracking_id(tracking_id: int, token: str = Depends(verify_jwt_token)):
    cache_key = f"parcel:{tracking_id}"
    cached_parcel = cache_get(cache_key)
    if cached_parcel:
        return JSONResponse(content=json.loads(cached_parcel), status_code=200)

    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://parcels5:8080/parcels/tracking/{tracking_id}") as response:
            if response.status == 200:
                parcel = await response.json()
                cache_set(cache_key, json.dumps(parcel))
                return JSONResponse(content=parcel, status_code=200)
            else:
                raise HTTPException(status_code=response.status, detail="Parcel not found")

@app.get("/deliveries/{delivery_id}")
async def get_delivery_by_id(delivery_id: str, token: str = Depends(verify_jwt_token)):
    cache_key = f"delivery:{delivery_id}"
    cached_delivery = cache_get(cache_key)
    if cached_delivery:
        return JSONResponse(content=json.loads(cached_delivery), status_code=200)

    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://deliveries5:8080/deliveries/{delivery_id}") as response:
            if response.status == 200:
                delivery = await response.json()
                cache_set(cache_key, json.dumps(delivery))
                return JSONResponse(content=delivery, status_code=200)
            else:
                raise HTTPException(status_code=response.status, detail="Delivery not found")

@app.get("/parcels/sender/{sender_id}")
async def get_parcels_by_sender_id(sender_id: int, token: str = Depends(verify_jwt_token)):
    cache_key = f"parcels:sender:{sender_id}"
    cached_parcels = cache_get(cache_key)
    if cached_parcels:
        return JSONResponse(content=json.loads(cached_parcels), status_code=200)

    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://parcels5:8080/parcels/sender/{sender_id}") as response:
            if response.status == 200:
                parcels = await response.json()
                cache_set(cache_key, json.dumps(parcels))
                return JSONResponse(content=parcels, status_code=200)
            else:
                raise HTTPException(status_code=response.status, detail="Parcels not found")

@app.get("/deliveries/user/{user_id}")
async def get_deliveries_by_user_id(user_id: int, token: str = Depends(verify_jwt_token)):
    cache_key = f"deliveries:user:{user_id}"
    cached_deliveries = cache_get(cache_key)
    if cached_deliveries:
        return JSONResponse(content=json.loads(cached_deliveries), status_code=200)

    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://deliveries5:8080/deliveries/user/{user_id}") as response:
            if response.status == 200:
                deliveries = await response.json()
                cache_set(cache_key, json.dumps(deliveries))
                return JSONResponse(content=deliveries, status_code=200)
            else:
                raise HTTPException(status_code=response.status, detail="Deliveries not found")

@app.get("/parcels/receiver/{receiver_id}")
async def get_parcels_by_receiver_id(receiver_id: int, token: str = Depends(verify_jwt_token)):
    cache_key = f"parcels:receiver:{receiver_id}"
    cached_parcels = cache_get(cache_key)
    if cached_parcels:
        return JSONResponse(content=json.loads(cached_parcels), status_code=200)

    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://parcels5:8080/parcels/receiver/{receiver_id}") as response:
            if response.status == 200:
                parcels = await response.json()
                cache_set(cache_key, json.dumps(parcels))
                return JSONResponse(content=parcels, status_code=200)
            else:
                raise HTTPException(status_code=response.status, detail="Parcels not found")

@app.get("/deliveries/receiver/{receiver_id}")
async def get_deliveries_by_receiver_id(receiver_id: int, token: str = Depends(verify_jwt_token)):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://deliveries5:8080/deliveries/receiver/{receiver_id}") as response:
            if response.status == 200:
                deliveries = await response.json()
                return JSONResponse(content=deliveries, status_code=200)
            else:
                raise HTTPException(status_code=response.status, detail="Deliveries not found")