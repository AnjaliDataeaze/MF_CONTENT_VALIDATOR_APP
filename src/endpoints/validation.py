from fastapi import APIRouter
from src import mf_validator
from fastapi import  File, UploadFile, Form
from typing import List
import shutil
import os
from pydantic import BaseModel
import json

router = APIRouter()

class S3Key(BaseModel):
    key: str


@router.post("/validation")
async def validation(file: UploadFile = File(...), program_type: str = Form(...), media_type: str = Form(...)):
    try:
        file_location = f"temp_files/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        if media_type =="pdf":
            value, response = mf_validator.validation(file_location, program_type)
            os.remove(file_location)
            return {"status": "SUCCESS" if value == 1 else "FAILED", "data": response}
        elif media_type =="GIF":
            value, response = mf_validator.gif_validation(file_location, program_type)
            os.remove(file_location)
            return {"status": "SUCCESS" if value == 1 else "FAILED", "data": response}
    except Exception as e:
        return {"status": "FAILED", "data": str(e)}

    
# @router.post("/video_validation")
# async def validation(file: UploadFile = File(...), program_type: str = Form(...), operation: List[str] = Form(...)):
#     try:
#         file_location = f"temp_files/{file.filename}"
#         os.makedirs(os.path.dirname(file_location), exist_ok=True)
#         with open(file_location, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         if len(operation)==2:
#             response = mf_validator.frame_analysis(file_location,program_type)
#             data = mf_validator.transcript(file_location, program_type)
#             os.remove(file_location)
#             return {"statu":"SUCCESS","DATA":[{"operation": "frame" , "data": response}, {"operation": "audio" , "data":data}]}
#         else:
#             if operation[0] == 'frame_analysis':
#                 response = mf_validator.frame_analysis(file_location,program_type)
#                 os.remove(file_location)
#                 return {"status": "SUCCESS" , "data": response}
            
#             elif operation[0] == 'audio_analysis':
#                 data = mf_validator.transcript(file_location, program_type)
#                 os.remove(file_location)
#                 return {"status":"Success", "Data":data}
                
#     except Exception as e:
#         return {"status": "FAILED", "data": str(e)}

@router.post("/video_validation")
async def validation(file: UploadFile = File(...), program_type: str = Form(...), operation:str = Form(...)):
    try:
        operations = json.loads(operation)
        print("operations-->", operations)
        print(type(operations))
        file_location = f"temp_files/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if len(operations)==2:
            response = mf_validator.frame_analysis(file_location,program_type)
            data1, data2 = mf_validator.transcript(file_location, program_type)
            os.remove(file_location)
            return {{"status": "frame" , "data": response}, {"status": "audio" , "Data": {"Data1": data1, "Data2":data2}}}
        else:
            if operations[0] == 'frame_analysis':
                response = mf_validator.frame_analysis(file_location,program_type)
                os.remove(file_location)
                return {"status": "SUCCESS" , "data": response}

            elif operations[0] == 'audio_analysis':
                print("calling Audio analysis")
                data1, data2 = mf_validator.transcript(file_location, program_type)
                os.remove(file_location)
                return {"Data1":data1,"Data2": data2}
    except Exception as e:
        return {"status": "FAILED", "data": str(e)}



@router.post("/gets3image")
async def gets3image(s3key:S3Key):
    response = mf_validator.get_image_url(s3key.key)
    return {"status": "SUCCESS" , "data": response}
        
        
    