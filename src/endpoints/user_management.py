from fastapi import APIRouter, Depends, HTTPException
from src import mf_user_management
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from src.dependency import get_current_user


router = APIRouter()

class AddUser(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    phone_number: str
    role : str

class Login(BaseModel):
    email: str
    password: str

class EditUser(BaseModel):
    email: str
    password: str
    role : str
    first_name: str
    last_name: str

class DeleteUser(BaseModel):
    email: str
   

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
    if get_current_user() ==1:
        value = mf_user_management.add_user(email=Add.email,
                                            password=Add.password,
                                            first_name=Add.first_name,
                                            last_name=Add.last_name,
                                            phone_number=Add.phone_number,
                                            role = Add.role
                                            )
        return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "User Added successfully !!!" if value == 1 else value}
    else:
        return RedirectResponse(url='/login')
    
  
@router.get("/list_user")
async def list_user():
    if get_current_user() ==1:
        value, data = mf_user_management.list_user()
        if value ==1:
            {"status": "SUCCESS", "data": data}
        else:
            {"status": "FAILED", "data": data}
    else:
        return RedirectResponse(url='/login')
    
    
@router.post("/edit_user")
async def edit_user(Edit: EditUser ):
    if get_current_user() ==1:
        value = mf_user_management.edit_user(email=Edit.email,
                                            password=Edit.password,
                                            role = Edit.role,
                                            first_name= Edit.first_name ,
                                            last_name=Edit.last_name
                                            )
        return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "User Added successfully !!!" if value == 1 else value}
    else:
        return RedirectResponse(url='/login')
    
@router.get("/delete_user")
async def delete_user(Delete: DeleteUser):
    if get_current_user() ==1:
        value = mf_user_management.delete_user(Delete.email)
        if value ==1:
            {"status": "SUCCESS", "data": "User deleted successfully"}
        else:
            {"status": "FAILED", "data": value}
    else:
        return RedirectResponse(url='/login')
    