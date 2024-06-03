from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from circuitbreaker import CircuitBreaker, CircuitBreakerError
import aiohttp
import jwt
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI()

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


JWT_SECRET_KEY = 'your_secret_key'

breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=10)

services = {
    "users": "http://users5:8080",
    "deliveries": "http://deliveries5:8080",
    "parcels": "http://parcels5:8080"
}

async def get_current_username(credentials: HTTPBasicCredentials = Depends()):
    return credentials.username

async def get_token(username: str, password: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{services['users']}/auth", auth=aiohttp.BasicAuth(username, password)) as response:
            if response.status == 200:
                token = await response.json()
                return token
            else:
                raise HTTPException(status_code=401, detail="Incorrect username or password")

async def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

@app.post("/auth/")
async def auth(username: str = Depends(get_current_username), password: str = Depends(get_current_username)):
    token = await get_token(username, password)
    return {"token": token}

@app.get("/users/{user_id}")
async def get_user(user_id: int, token: str = Depends(verify_jwt_token)):
    try:
        with breaker:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{services['users']}/users/{user_id}") as response:
                    return await response.json()
    except CircuitBreakerError:
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/deliveries/{delivery_id}")
async def get_delivery(delivery_id: str, token: str = Depends(verify_jwt_token)):
    try:
        with breaker:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{services['deliveries']}/deliveries/{delivery_id}") as response:
                    return await response.json()
    except CircuitBreakerError:
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/parcels/{parcel_id}")
async def get_parcel(parcel_id: str, token: str = Depends(verify_jwt_token)):
    try:
        with breaker:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{services['parcels']}/parcels/{parcel_id}") as response:
                    return await response.json()
    except CircuitBreakerError:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
@app.get("/parcels/")
async def get_all_parcels(token: str = Depends(verify_jwt_token)):
    try:
        with breaker:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{services['parcels']}/parcels", headers={"Authorization": f"Bearer {token}"}) as response:
                    return await response.json()
    except CircuitBreakerError:
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/deliveries/")
async def get_all_deliveries(token: str = Depends(verify_jwt_token)):
    try:
        with breaker:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{services['deliveries']}/deliveries", headers={"Authorization": f"Bearer {token}"}) as response:
                    return await response.json()
    except CircuitBreakerError:
        raise HTTPException(status_code=503, detail="Service unavailable")