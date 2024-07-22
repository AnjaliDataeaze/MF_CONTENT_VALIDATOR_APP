from fastapi import APIRouter
from src import mf_validator
from pydantic import BaseModel
from typing import List


router = APIRouter()
    
class AddProgram(BaseModel):
    name: str
    description: str
    rules : List[str]
    created_by : str

class DeleteProgram(BaseModel):
    program_id: int

class EditProgram(BaseModel):
    program_id: int
    name: str
    description: str
    rules : List[str]



@router.get("/list_programs")
def list_programs():
    return mf_validator.list_programs() 


@router.post("/add_program")
async def add_program(program: AddProgram):
    return mf_validator.add_program(program.name, program.description, program.rules, program.created_by)


@router.post("/edit_program")
async def edit_program(program: EditProgram):
    return mf_validator.edit_program(program.program_id, program.name, program.description, program.rules)


@router.delete("/delete_program")
def delete_program(program: DeleteProgram):
    return mf_validator.delete_program(program.program_id)


