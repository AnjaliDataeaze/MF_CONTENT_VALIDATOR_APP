from fastapi import APIRouter
from src import mf_validator
from pydantic import BaseModel
from typing import List


router = APIRouter()
    
class AddProgram(BaseModel):
    name: str
    description: str
    rules : List[str]
                
class DeleteProgram(BaseModel):
    program_id: int

class EditProgram(BaseModel):
    program_id: int
    name: str
    description: str
    rules : List[str]




@router.get("/list_programs")
def list_programs():
    value, data = mf_validator.list_programs()
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": data}
    
    
@router.post("/add_program")
async def add_program(program: AddProgram):
    value = mf_validator.add_program(program.name, program.description, program.rules)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Program added successfully !!!" if value == 1 else value}
    
    
@router.post("/edit_program")
async def edit_program(program: EditProgram):
    value = mf_validator.edit_program(program.program_id, program.name, program.description, program.rules)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Program edited successfully !!!" if value == 1 else value}
    
@router.delete("/delete_program")
def delete_program(program: DeleteProgram):
    value = mf_validator.delete_program(program.program_id)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Program deleted successfully !!!" if value == 1 else value}
    