from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List
import secrets

app = FastAPI()

engine = create_engine('postgresql://postgres:postgres@postgres:5432/archdb')
Base = declarative_base()


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


security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(
        credentials.username, "stanleyjobson")
    correct_password = secrets.compare_digest(
        credentials.password, "swordfish")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")
    return credentials.username


@app.get("/users", response_model=List[UserResponse])
async def get_users():
    users = session.query(User).all()
    return [UserResponse(id=user.id, login=user.login, first_name=user.first_name, last_name=user.last_name, address=user.address) for user in users]


@app.post("/users", response_model=UserResponse)
async def create_user(user: UserRequest):
    user_obj = User(**user.dict())
    session.add(user_obj)
    session.commit()
    return UserResponse(id=user_obj.id, login=user_obj.login, first_name=user_obj.first_name, last_name=user_obj.last_name, address=user_obj.address)


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = session.query(User).get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, login=user.login, first_name=user.first_name, last_name=user.last_name, address=user.address)


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserRequest):
    user_obj = session.query(User).get(user_id)
    if user_obj is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict().items():
        setattr(user_obj, key, value)
    session.commit()
    return UserResponse(id=user_obj.id, login=user_obj.login, first_name=user_obj.first_name, last_name=user_obj.last_name, address=user_obj.address)


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    user = session.query(User).get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return JSONResponse(status_code=200, content={"message": "User deleted"})


@app.get("/users/search", response_model=List[UserResponse])
async def search_users(query: str):
    users = session.query(User).filter(User.first_name.like(
        f"%{query}%") | User.last_name.like(f"%{query}%")).all()
    return [UserResponse(id=user.id, login=user.login, first_name=user.first_name, last_name=user.last_name, address=user.address) for user in users]
