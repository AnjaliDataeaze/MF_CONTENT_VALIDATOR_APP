from fastapi import APIRouter, Depends, HTTPException
from src import mf_validator
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, Form
import shutil
import os
from src.dependency import get_current_user

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

@router.post("/validation")
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
            os.remove(file_location)
            return {"status": "SUCCESS" if value == 1 else "FAILED", "data": data}
        # Delete the file after processing
        
    except Exception as e:
        return {"status": "FAILED", "data": str(e)}

