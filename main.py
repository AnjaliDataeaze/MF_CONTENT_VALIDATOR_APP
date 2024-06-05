from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src import mf_validator
import psycopg2
app = FastAPI()
print("Working")


# Configure CORS
origins = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",  # React development server (alternative)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


#####################################################

@app.get("/list_programs")
def list_programs():
    value, data = mf_validator.list_programs()
    if value == 1:
        # print("data",data)
        # print({"status": "SUCCESS", "data": data})
        return {"status": "SUCCESS", "data": data}
    else:
        return {"status": "FAILED", "data": data}

  
@app.post("/add_program")
async def add_program(request: Request):
    body = await request.json()
    name = body.get('name')
    description = body.get('description')
    value = mf_validator.add_program(name, description)
    if value == 1:
        return {"status": "SUCCESS", "data": "Program added successfully !!!"}
    else:
        return {"status": "FAILED", "data": value}



# @app.get("/edit_program")
# def edit_program(program_id, new_name, new_description):
#     value = mf_validator.edit_program(program_id, new_name, new_description)
#     if value ==1:
#         return {"status":"SUCCESS","data":"Program Updated successfully !!!"}
#     else:
#         return {"status":"FAILED","data":value}

@app.post("/edit_program/{program_id}")
async def edit_program(program_id: int, request: Request):
    body = await request.json()
    name = body.get('name')
    description = body.get('description')
    value = mf_validator.edit_program(program_id, name, description)
    if value == 1:
        return {"status": "SUCCESS", "data": "Program edited successfully !!!"}
    else:
        return {"status": "FAILED", "data": value}

    


@app.get("/delete_program")
async def delete_program(program_id: int):
    value = mf_validator.delete_program(program_id=program_id)
    if value == 1:
        return {"status": "SUCCESS", "data": "Program deleted successfully !!!"}
    else:
        return {"status": "FAILED", "data": value}
    

######################################### API FOR RULE ####################################################
 

@app.get("/list_rules")
def list_rules():
    value, data = mf_validator.list_rules()
    if value==1:
        return {"status":"SUCCESS","data":data}
    else:
        return {"status":"FAILED","data":data}

@app.get("/list_rules_by_program")

def list_rules_by_program():
    value, data = mf_validator.list_rules_by_program()
    if value==1:
        return {"status":"SUCCESS","data":data}
    else:
        return {"status":"FAILED","data":data}

#commented by me
# @app.get("/add_rule")
# def add_rule(rulename, media_type, description, program_id):
#     print(f"rulename", rulename)
#     print(f"program_id", program_id)
#     value = mf_validator.add_rule(rulename, media_type, description, program_id)

#     if value==1:
#        return {"status":"SUCCESS","data":"Rule added successfully !!!"}
#     else:
#         return {"status":"FAILED","data":value}

@app.post("/add_rule")
async def add_rule(request: Request):
    body = await request.json()
    rulename = body.get('rulename')
    media_type = body.get('media_type')
    description = body.get('description')
    program_type = body.get('program_type')
    disclaimer = body.get('disclaimer')
    print("body is****************************************************************", body)
    value = mf_validator.add_rule(rulename, media_type, description, program_type, disclaimer)
    if value == 1:
        return {"status": "SUCCESS", "data": "Rule added successfully !!!"}
    else:
        return {"status": "FAILED", "data": value}
    
# @app.get("/add_rule_to_program")
# def add_rule_to_program(rule_id, program_id):
#     value = mf_validator.add_rule_to_program(rule_id, program_id)
#     if value==1:
#        return {"status":"SUCCESS","data":"Rule added to program successfully !!!"}
#     else:
#         return {"status":"FAILED","data":value}


# @app.get("/edit_rule")
# def edit_rule(rule_id, rulename, media_type, description):
#     value = mf_validator.edit_rule(rule_id, rulename, media_type, description)
#     if value==1:
#         return {"status":"SUCCESS","data":"Rule Updated successfully !!!"}
#     else:
#         return {"status":"FAILED","data":value}

@app.post("/edit_rule/{rule_id}")
async def edit_rule(rule_id: int, request: Request):
    body = await request.json()
    rulename = body.get('rulename')
    description = body.get('description')
    disclaimer = body.get('disclaimer')
    print("ALL Values: ", rulename, description, disclaimer, rule_id)
    value = mf_validator.edit_rule(rulename, description, disclaimer, rule_id)
    if value == 1:
        return {"status": "SUCCESS", "data": "Rule updated successfully !!!"}
    else:
        return {"status": "FAILED", "data": value}
    
    
@app.get("/delete_rule/{rule_id}")
def delete_rule(rule_id: int):
    value = mf_validator.delete_rule(rule_id)
    if value == 1:
        return {"status": "SUCCESS", "data": "Rule deleted successfully !!!"}
    else:
        return {"status": "FAILED", "data": value}

###################################### API FOR DISCLAIMER ##################################################

@app.get("/list_disclaimer")
def list_disclaimers():
    value , data= mf_validator.list_disclaimers()
    if value ==1:
        return {"status":"SUCCESS","data":value}
    else:
        return {"status":"FAILED","data":value}

@app.get("/add_disclaimer")
def add_disclaimer(name_of_disclaimer, rule_id, actual_disclaimer):
    value = mf_validator.add_disclaimer(name_of_disclaimer, rule_id, actual_disclaimer)
    if value ==1:
        return {"status":"SUCCESS","data":"Discliamer added successfully !!!"}
    else:
        return {"status":"FAILED","data":value}
    
@app.get("/edit_disclaimer")
def edit_disclaimer(disclaimer_id, rule_id, actual_disclaimer):
    value = mf_validator.edit_rule(disclaimer_id, rule_id, actual_disclaimer)
    if value ==1:
        return {"status":"SUCCESS","data":"Disclaimer Updated successfully !!!"}
    else:
        return {"status":"FAILED","data":value}
    

@app.get("/delete_disclaimer")
def delete_disclaimer(disclaimer_id):
    value = mf_validator.delete_rule(disclaimer_id)
    if value==1:
        return {"status":"SUCCESS","data":"Disclaimer deleted successfully !!!"}
    else:
        return {"status":"FAILED","data":value}

########################### VALIDATION #############################

@app.get("/validation")
def validation(file_path):
    value, response = mf_validator.validation(file_path=file_path)
    if value==1:
        return {"status":"SUCCESS","data":response}
    else:
        return {"status":"FAILED","data":response}