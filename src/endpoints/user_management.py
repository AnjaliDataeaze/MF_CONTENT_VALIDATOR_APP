from fastapi import APIRouter, Depends, HTTPException
from src import mf_user_management
from pydantic import BaseModel

router = APIRouter()

class AddUser(BaseModel):
    user_name: str
    email: str
    password: str
    first_name: str
    last_name: str
    phone_number: str
    address: str

class Login(BaseModel):
    user_name : int
    email: str
    password: str



@router.post("/login")
async def add_user(Log: Login):
    value = mf_user_management.login(username=Log.user_name, email=Log.email, password=Log.password)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Logged in  successfully !!!" if value == 1 else value}

@router.post("/add_user")
async def add_user(Add: AddUser ):
    value = mf_user_management.add_user(username=Add.user_name,
                                        email=Add.email,
                                        password=Add.password,
                                        first_name=Add.first_name,
                                        last_name=Add.last_name,
                                        phone_number=Add.phone_number,
                                        address=Add.address)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "User Added successfully !!!" if value == 1 else value}
