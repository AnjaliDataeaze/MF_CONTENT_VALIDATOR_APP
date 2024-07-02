from fastapi import APIRouter, Depends, HTTPException
from src import mf_validator
from pydantic import BaseModel
from src.dependency import get_current_user
from fastapi.responses import RedirectResponse

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)
class AddRule(BaseModel):
    rulename: str
    media_type: str
    description: str
    program_type: str
    disclaimer: str

class EditRule(BaseModel):
    rule_id : int
    rulename: str
    description: str
    disclaimer: str

class DeleteRule(BaseModel):
    rule_id: int

class ListRulesByProgram(BaseModel):
    program_id: int



@router.get("/list_rules")
def list_rules():
    if get_current_user() == 1:
        value, data = mf_validator.list_rules()
        return {"status": "SUCCESS" if value == 1 else "FAILED", "data": data}
    else:
        return RedirectResponse(url='/login')
    
@router.post("/list_rules_by_program")
def list_rules_by_program(rule: ListRulesByProgram):
    if get_current_user() ==1:
        value, data = mf_validator.list_rules_by_program(rule.program_id)
        return {"status": "SUCCESS" if value == 1 else "FAILED", "data": data}
    else:
        return RedirectResponse(url='/login')
    
@router.post("/add_rule")
async def add_rule(rule: AddRule):
    if get_current_user() ==1:
        value = mf_validator.add_rule(rule.rulename, rule.media_type, rule.description, rule.program_type, rule.disclaimer)
        return {"status": "SUCCESS" if value == 1 
                else "FAILED", "data": "Rule added successfully !!!" if value == 1 else value}
    else:
        return RedirectResponse(url='/login')
    

@router.post("/edit_rule")
async def edit_rule(rule: EditRule):
    if get_current_user() ==1:
        value = mf_validator.edit_rule(rule.rule_id, rule.rulename, rule.description, rule.disclaimer)
        return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Rule updated successfully !!!" if value == 1 else value}
    else:
        return RedirectResponse(url='/login')
    
@router.delete("/delete_rule")
def delete_rule(rule : DeleteRule):
    if get_current_user() ==1:
        value = mf_validator.delete_rule(rule.rule_id)
        return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Rule deleted successfully !!!" if value == 1 else value}
    else:
        return RedirectResponse(url='/login')