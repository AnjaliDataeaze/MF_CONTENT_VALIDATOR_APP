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

class Login(BaseModel):
    user_name : int
    email: str
    password: str



# @router.post("/user_login")
# async def add_user(Log: Login):
#     value = mf_user_management.standard_loginlogin(username=Log.user_name, email=Log.email, password=Log.password)
#     if value ==1:
#         return {"status": "SUCCESS", "data": "Login Successful"}
#     elif value == 2:
#         return {"status": "FAILED", "data": "Wrong Credentials"}
#     else:
#         return {"status": "NOT_FOUND", "data": "User Not Found"}

@router.post("/add_user")
async def add_user(Add: AddUser ):
    value = mf_user_management.add_user(username=Add.user_name,
                                        email=Add.email,
                                        password=Add.password,
                                        first_name=Add.first_name,
                                        last_name=Add.last_name,
                                        phone_number=Add.phone_number,
                                        )
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "User Added successfully !!!" if value == 1 else value}

@router.get("/list_user")
async def list_user():
    value, data = mf_user_management.list_user()
    if value ==1:
        {"status": "SUCCESS", "data": data}
    else:
        {"status": "FAILED", "data": data}
