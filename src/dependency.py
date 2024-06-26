from starlette.requests import Request
from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user
