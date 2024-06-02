from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List
from passlib.hash import bcrypt
import jwt
import time

app = FastAPI()

engine = create_engine('postgresql://postgres:postgres@postgres:5432/archdb')
Base = declarative_base()

JWT_SECRET_KEY = 'your_secret_key'  

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    address = Column(Text)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

class UserRequest(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str
    address: str

class UserResponse(BaseModel):
    id: int
    login: str
    first_name: str
    last_name: str
    address: str

class TokenResponse(BaseModel):
    access_token: str

security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    user = session.query(User).filter_by(login=credentials.username).first()
    if not user:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")
    if not bcrypt.verify(credentials.password, user.password): 
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")
    return credentials.username, credentials.password

def generate_jwt_token(username, password):
    payload = {
        'sub': username,
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600  # 1 hour
    }
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return encoded_jwt

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

@app.post("/auth", response_model=TokenResponse)
async def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    username, password = get_current_username(credentials)
    access_token = generate_jwt_token(username, password)
    return TokenResponse(access_token=access_token)

@app.get("/users", response_model=List[UserResponse])
async def get_users(token: str = Depends(verify_jwt_token)):
    users = session.query(User).all()
    return [UserResponse(id=user.id, login=user.login, first_name=user.first_name, last_name=user.last_name, address=user.address) for user in users]

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserRequest):
    password = bcrypt.hash(user.password)
    user_obj = User(**user.dict())
    user_obj.password = password
    session.add(user_obj)
    session.commit()
    print(user_obj.id)
    return UserResponse(id=user_obj.id, login=user_obj.login, first_name=user_obj.first_name, last_name=user_obj.last_name, address=user_obj.address)

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, token: str = Depends(verify_jwt_token)):
    user = session.query(User).get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, login=user.login, first_name=user.first_name, last_name=user.last_name, address=user.address)

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserRequest, token: str = Depends(verify_jwt_token)):
    user_obj = session.query(User).get(user_id)
    if user_obj is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict().items():
        setattr(user_obj, key, value)
    session.commit()
    return UserResponse(id=user_obj.id, login=user_obj.login, first_name=user_obj.first_name, last_name=user_obj.last_name, address=user_obj.address)

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, token: str = Depends(verify_jwt_token)):
    user = session.query(User).get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"detail": "User deleted successfully"}


@app.get("/users/login/{login}", response_model=UserResponse)
async def get_user_by_login(login: str, token: str = Depends(verify_jwt_token)):
    user = session.query(User).filter_by(login=login).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, login=user.login, first_name=user.first_name, last_name=user.last_name, address=user.address)


@app.get("/users/name/{name}", response_model=List[UserResponse])
async def search_users_by_name(name: str, token: str = Depends(verify_jwt_token)):
    users = session.query(User).filter(User.first_name.like(
        f"%{name}%") | User.last_name.like(f"%{name}%")).all()
    return [UserResponse(id=user.id, login=user.login, first_name=user.first_name, last_name=user.last_name, address=user.address) for user in users]
