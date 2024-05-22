from fastapi import FastAPI
from src import mf_validator
app = FastAPI()


## api for programs

@app.get("/programs")
def list_programs():
    value = mf_validator.list_programs
    return  {"status":"SUCCESS","data":value}

@app.get("/add_program")
def add_program(name, description):
    
    mf_validator.add_program(name, description)
    return {"status":"SUCCESS","data":"Program added successfully !!!"}

@app.get("/edit_program")
def edit_program():
    value = mf_validator.edit_program()
    return value

@app.get("/delete_program")
def delete_program():
    value = mf_validator.delete_program()
    return value


## api for rule

@app.get("/rule")
def list_rules():
    value = mf_validator.list_rules()
    return {"status":"SUCCESS","data":value}

@app.get("/add_rule")
def add_rule():
    value = mf_validator.add_rule()
    return value

@app.get("/edit_rule")
def edit_rule():
    value = mf_validator.edit_rule()
    return value

@app.get("/delete_rule")
def delete_rule():
    value = mf_validator.delete_rule()
    return value

## api for disclaimer 

@app.get("/disclaimer")
def list_disclaimers():
    value = mf_validator.list_rules()
    return value

@app.get("/add_disclaimer")
def add_disclaimer():
    value = mf_validator.add_rule()
    return value

@app.get("/edit_disclaimer")
def edit_disclaimer():
    value = mf_validator.edit_rule()
    return value

@app.get("/delete_disclaimer")
def delete_disclaimer():
    value = mf_validator.delete_rule()
    return value

