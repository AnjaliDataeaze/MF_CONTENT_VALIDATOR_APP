from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src import mf_validator
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil

print("Working")
app = FastAPI()
# app = FastAPI(__name__,
#             static_folder='./Frontend/build',
#             static_url_path='/')

# CORS configuration
# origins = ["http://65.2.98.191:8000/", "http://localhost:3000", "http://65.2.98.191:8000/", "http://localhost:3000/", "http://65.2.98.191:3000", "http://127.0.0.1:3000", "http://127.0.0.1:8000"]
# origins = ["http://65.2.98.191:8000/", "http://localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type"]
)

# Serve static files
app.mount("/static", StaticFiles(directory="build/static"), name="static")

@app.get("/programtypes")
async def chat():
    return HTMLResponse(content=open("build/index.html").read())

@app.get("/rules")
async def chat1():
    return HTMLResponse(content=open("build/index.html").read())
@app.get("/validate-content")
async def chat2():
    return HTMLResponse(content=open("build/index.html").read())
@app.get("/")
async def root():

    return HTMLResponse(content=open("build/index.html").read())
    
    
# Program Models
class AddProgram(BaseModel):
    name: str
    description: str

class DeleteProgram(BaseModel):
    program_id: int

class EditProgram(BaseModel):
    program_id: int
    name: str
    description: str

# Rule Models
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

# Disclaimer Models

class AddDisclaimer(BaseModel):
    rule_id: int
    actual_disclaimer: str

class EditDisclaimer(BaseModel):
    disclaimer_id: int
    rule_id: int
    actual_disclaimer: str

class DeleteDisclaimer(BaseModel):
    disclaimer_id: int

# Validation Models

class Validation(BaseModel):
    program_type: str
    media_type : str


# Video Transcrition Models

class VideoTranscrition(BaseModel):
    video_path: str

# Program Endpoints
@app.get("/list_programs")
def list_programs():
    value, data = mf_validator.list_programs()
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": data}

@app.post("/add_program")
async def add_program(program: AddProgram):
    value = mf_validator.add_program(program.name, program.description)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Program added successfully !!!" if value == 1 else value}

@app.post("/edit_program")
async def edit_program(program: EditProgram):

    value = mf_validator.edit_program(program.program_id, program.name, program.description)

    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Program edited successfully !!!" if value == 1 else value}

@app.delete("/delete_program")
def delete_program(program: DeleteProgram):
    value = mf_validator.delete_program(program.program_id)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Program deleted successfully !!!" if value == 1 else value}

# Rule Endpoints
@app.get("/list_rules")
def list_rules():
    value, data = mf_validator.list_rules()
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": data}

@app.post("/list_rules_by_program")
def list_rules_by_program(rule: ListRulesByProgram):
    value, data = mf_validator.list_rules_by_program(rule.program_id)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": data}

@app.post("/add_rule")
async def add_rule(rule: AddRule):
    value = mf_validator.add_rule(rule.rulename, rule.media_type, rule.description, rule.program_type, rule.disclaimer)
    return {"status": "SUCCESS" if value == 1 
            else "FAILED", "data": "Rule added successfully !!!" if value == 1 else value}

@app.post("/edit_rule")
async def edit_rule(rule: EditRule):
    value = mf_validator.edit_rule(rule.rule_id, rule.rulename, rule.description, rule.disclaimer)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Rule updated successfully !!!" if value == 1 else value}

@app.delete("/delete_rule")
def delete_rule(rule : DeleteRule):
    value = mf_validator.delete_rule(rule.rule_id)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Rule deleted successfully !!!" if value == 1 else value}

# Disclaimer Endpoints

@app.post("/add_disclaimer")
async def add_disclaimer(disclaimer: AddDisclaimer):
    value = mf_validator.add_disclaimer(disclaimer.rule_id, disclaimer.actual_disclaimer)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Disclaimer added successfully !!!" if value == 1 else value}

@app.post("/edit_disclaimer")
async def edit_disclaimer(disclaimer: EditDisclaimer):
    value = mf_validator.edit_disclaimer(disclaimer.disclaimer_id, disclaimer.rule_id, disclaimer.actual_disclaimer)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Disclaimer updated successfully !!!" if value == 1 else value}

@app.delete("/delete_disclaimer")
def delete_disclaimer(disclaimer: DeleteDisclaimer):
    value = mf_validator.delete_disclaimer(disclaimer.disclaimer_id)
    return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "Disclaimer deleted successfully !!!" if value == 1 else value}


@app.post("/validation")
async def validation(file: UploadFile = File(...), program_type: str = Form(...), media_type: str = Form(...)):
    try:
        file_location = f"temp_files/{file.filename}"
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_location), exist_ok=True)

        # Save the file to the specified location
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        if media_type =="pdf":
            value, response = mf_validator.validation(file_location, program_type)
            # list_2d = [inner for outer in response for inner in outer]
            os.remove(file_location)
            return {"status": "SUCCESS" if value == 1 else "FAILED", "data": response}
        elif media_type == "Video":
            value, data = mf_validator.transcript(file_location)
            print("Data: ---------: ",data)
            os.remove(file_location)
            return {"status": "SUCCESS" if value == 1 else "FAILED", "data": data}
        # Delete the file after processing
        
    except Exception as e:
        return {"status": "FAILED", "data": str(e)}
