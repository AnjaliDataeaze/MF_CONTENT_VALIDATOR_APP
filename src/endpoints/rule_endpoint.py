from fastapi import APIRouter, HTTPException, Query
from src import mf_validator
from pydantic import BaseModel

router = APIRouter()
class AddRule(BaseModel):
    rulename: str
    media_type: str
    description: str
    disclaimer: str
    assigned_to: str
    ruleStatus: str
    created_by: str

class EditRule(BaseModel):
    rule_id : int
    rulename: str
    description: str
    disclaimer: str

class DeleteRule(BaseModel):
    rule_id: int

class ListRulesByProgram(BaseModel):
    program_id: int

class ProgramId(BaseModel):
    program_id: int

class ChangeRuleStatusRequest(BaseModel):
    rule_id: int
    status: str


@router.get("/list_rules")
def list_rules(status: str = None):
    return mf_validator.list_rules(status)


@router.get("/filter_rules")
def filter_rules(search: str = Query(None), status: str = Query(None)):
    return mf_validator.filter_rules(search, status)


@router.post("/add_rule")
async def add_rule(rule: AddRule):
    return mf_validator.add_rule(rule.rulename, rule.media_type, rule.description, rule.disclaimer, rule.assigned_to, rule.ruleStatus,rule.created_by)
    

@router.post("/edit_rule")
async def edit_rule(rule: EditRule):
    return mf_validator.edit_rule(rule.rule_id, rule.rulename, rule.description, rule.disclaimer)


@router.delete("/delete_rule")
def delete_rule(rule: DeleteRule):
    return mf_validator.delete_rule(rule.rule_id)


@router.post("/get_mapped_rules")
async def get_mapped_rules(program_id: ProgramId):
    return mf_validator.get_mapped_rules(program_id.program_id)

@router.post("/change_rule_status")
def change_rule_status(request: ChangeRuleStatusRequest):
    try:
        return mf_validator.change_rule_status(request.rule_id, request.status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   