from fastapi import APIRouter
from src import mf_user_management
from pydantic import BaseModel


router = APIRouter()

class AddUser(BaseModel):
    email: str
    password: str
    firstName: str
    lastName: str
    phoneNumber: str
    role : str
    status: str

class Login(BaseModel):
    email: str
    password: str

class EditUser(BaseModel):
    firstName: str
    lastName: str
    email: str
    phoneNumber: str
    role : str
    status: str
    

class DeleteUser(BaseModel):
    user_id: int
   

@router.post("/add_user")
async def add_user(Add: AddUser ):
    value = mf_user_management.add_user(email=Add.email,
                                        password=Add.password,
                                        first_name=Add.firstName,
                                        last_name=Add.lastName,
                                        phone_number=Add.phoneNumber,
                                        role = Add.role,
                                        status = Add.status
                                        )
    
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "User Added successfully !!!" if value == 1 else value}
    
  
@router.get("/list_users")
async def list_user():
    value, data = mf_user_management.list_user()
    if value == 1:
        return {"status": "SUCCESS", "data": data}
    else:
        return {"status": "FAILED", "data": data}
   
@router.get("/filter_user")
async def filter_user(search: str):
    result = mf_user_management.filter_user(search)
    return result


@router.post("/edit_user")
async def edit_user(Edit: EditUser ):
    value = mf_user_management.edit_user(first_name= Edit.firstName ,
                                         last_name=Edit.lastName,
                                         email=Edit.email,
                                         phone_number = Edit.phoneNumber,
                                         role = Edit.role,
                                         status= Edit.status
                                        )
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "User updated successfully !!!" if value == 1 else value}
    
    
@router.delete("/delete_user")
async def delete_user(Delete: DeleteUser):
    value = mf_user_management.delete_user(Delete.user_id)
    if value ==1:
        return {"status": "SUCCESS", "data": "User deleted successfully"}
    else:
        return {"status": "FAILED", "data": value}
    