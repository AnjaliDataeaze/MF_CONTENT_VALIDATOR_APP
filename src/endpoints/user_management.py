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
    return mf_user_management.add_user(
            email=Add.email, 
            password=Add.password, 
            first_name=Add.firstName, 
            last_name=Add.lastName, 
            phone_number=Add.phoneNumber, 
            role = Add.role, 
            status = Add.status
            )
    
@router.get("/list_users")
async def list_users():
    return mf_user_management.list_users()



@router.get("/filter_user")
async def filter_user(search: str):
    return mf_user_management.filter_user(search)

 
@router.post("/edit_user")
async def edit_user(edit: EditUser):
    return mf_user_management.edit_user(
        first_name=edit.firstName,
        last_name=edit.lastName,
        email=edit.email,
        phone_number=edit.phoneNumber,
        role=edit.role,
        status=edit.status
    )


@router.delete("/delete_user")
async def delete_user(Delete: DeleteUser):
    return mf_user_management.delete_user(Delete.user_id)