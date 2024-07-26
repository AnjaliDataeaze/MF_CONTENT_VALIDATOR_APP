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

### for postman
'''    
@router.post("/video_validation")
async def validation(file: UploadFile = File(...), program_type: str = Form(...), operation: List[str] = Form(...)):
    try:
        file_location = f"temp_files/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if len(operation)==2:
            response = mf_validator.frame_analysis(file_location,program_type)
            data = mf_validator.transcript(file_location, program_type)
            os.remove(file_location)
            if response is None and data is None:
                return {"frame": {"status": "FAILED", "data": "Failed for frame analysis"}, "audio": {"status": "FAILED", "data": "Failed for audio analysis"}}
            elif data is None and response is not None:
                return {"frame": {"status": "FAILED", "data": "Failed for frame analysis"}, "audio": {"status": "SUCCESS", "data": data}}
            elif response is None and data is not None:
                return {"frame": {"status": "SUCCESS", "data": response}, "audio": {"status": "FAILED", "data": "Failed for audio analysis"}}
            else:
                return {"frame": {"status": "SUCCESS", "data": response}, "audio": {"status": "SUCCESS", "data": data}}

        else:
            if operation[0] == 'frame_analysis':
                response = mf_validator.frame_analysis(file_location,program_type)
                os.remove(file_location)
                
                if response is None:
                    return {"status": "FAILED" , "Data": "SYSTEM FAILED"}
                else:
                    print("++++++++=============================")
                    print(response)
                    return {"status": "SUCCESS" , "Data": response}
            
            elif operation[0] == 'audio_analysis':
                data = mf_validator.transcript(file_location, program_type)
                os.remove(file_location)
                if data is None:
                    return {"status": "FAILED" , "Data": "SYSTEM FAILED"}
                else:
                    return {"status":"SUCCESS", "Data":data}
                
    except Exception as e:
        return {"status": "FAILED", "Data": str(e)}
'''


### for build

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
            data = mf_validator.transcript(file_location, program_type)
            os.remove(file_location)
            if response is None and data is None:
                return {"frame": {"status": "FAILED", "data": "Failed for frame analysis"}, "audio": {"status": "FAILED", "data": "Failed for audio analysis"}}
            elif data is None and response is not None:
                return {"frame": {"status": "FAILED", "data": "Failed for frame analysis"}, "audio": {"status": "SUCCESS", "data": data}}
            elif response is None and data is not None:
                return {"frame": {"status": "SUCCESS", "data": response}, "audio": {"status": "FAILED", "data": "Failed for audio analysis"}}
            else:
                return {"frame": {"status": "SUCCESS", "data": response}, "audio": {"status": "SUCCESS", "data": data}}

        else:
            if operations[0] == 'frame_analysis':
                response = mf_validator.frame_analysis(file_location,program_type)
                os.remove(file_location)
                if response is None:
                    return {"status": "FAILED" , "Data": "SYSTEM FAILED"}
                else:
                    print("++++++++=============================")
                    print(response)
                    return {"status": "SUCCESS" , "Data": response}

            elif operations[0] == 'audio_analysis':
                print("calling Audio analysis")
                data = mf_validator.transcript(file_location, program_type)
                os.remove(file_location)
                if data is None:
                    return {"status": "FAILED" , "Data": "SYSTEM FAILED"}
                else:
                    return {"status":"SUCCESS", "Data":data}
    except Exception as e:
        return {"status": "FAILED", "data": str(e)}



@router.post("/gets3image")
async def gets3image(s3key:S3Key):
    response = mf_validator.get_image_url(s3key.key)
    return {"status": "SUCCESS" , "data": response}
        
        
    