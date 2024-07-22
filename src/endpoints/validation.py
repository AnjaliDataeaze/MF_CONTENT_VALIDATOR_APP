from fastapi import APIRouter
from src import mf_validator
from fastapi import  File, UploadFile, Form

import shutil
import os
from pydantic import BaseModel


router = APIRouter()

class S3Key(BaseModel):
    key: str


@router.post("/validation")
async def validation(file: UploadFile = File(...), program_type: str = Form(...), media_type: str = Form(...)):
    try:
        file_location = f"temp_files/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)

        # Save the file to the specified location
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        if media_type =="pdf":
            value, response = mf_validator.validation(file_location, program_type)
            os.remove(file_location)
            return {"status": "SUCCESS" if value == 1 else "FAILED", "data": response}
        # elif media_type == "Video":
        #     value, data = mf_validator.transcript(file_location)
        #     os.remove(file_location)
        #     return {"status": "SUCCESS" if value == 1 else "FAILED", "data": data}
        elif media_type =="GIF":
            value, response = mf_validator.gif_validation(file_location, program_type)
            os.remove(file_location)
            return {"status": "SUCCESS" if value == 1 else "FAILED", "data": response}
        
    except Exception as e:
        return {"status": "FAILED", "data": str(e)}

    
@router.post("/video_validation")
async def validation(file: UploadFile = File(...),program_type: str = Form(...), operation: str = Form(...)):
    try:
        print("Operation-->", operation)
        file_location = f"temp_files/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print("********************")
        ###--- frame analysis --- ###
        # if len(operation)==2:
        #     response = mf_validator.frame_analysis(file_location,program_type)
        #     value, data = mf_validator.transcript(file_location, program_type)

        #     return {"status": "SUCCESS" , "data": response}
        # else:
        #     if operation[0] == 'frame_analysis':
        #         response = mf_validator.frame_analysis(file_location,program_type)
        #         os.remove(file_location)
        #         return {"status": "SUCCESS" , "data": response}
            
        if operation == 'audio_analysis':
            print("$$$$$$$$$$$$$$$$$$$$$$$$$")
            data = mf_validator.transcript(file_location, program_type)
            os.remove(file_location)
            # return {"status": "SUCCESS" if value == 1 else "FAILED", "data": data}
            return data
    except Exception as e:
        return {"status": "FAILED", "data": str(e)}


@router.post("/gets3image")
async def gets3image(s3key:S3Key):
    response = mf_validator.get_image_url(s3key.key)
    return {"status": "SUCCESS" , "data": response}
        
        
    