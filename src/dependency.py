from starlette.requests import Request
from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

# def get_current_user(request: Request):
#     user = request.session.get('user')
#     if not user:
#         raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")
#     return user

def get_current_user(request: Request):
    user = request.session.get('user') 
    if user !=1 :
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    return user  
