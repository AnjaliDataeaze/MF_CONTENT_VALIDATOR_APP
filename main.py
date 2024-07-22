from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from src.config.credentials import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URL, BUILD_PATH
from src.endpoints import program, validation, user_management
from src.endpoints import rule_endpoint
from src.mf_user_management import standard_login
from fastapi import Form, HTTPException, Response
from pydantic import BaseModel
from starlette.status import HTTP_302_FOUND


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="add any string...")

def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=HTTP_302_FOUND, detail="Unauthorized", headers={"Location": "/login"})
    return user

class UserLogin(BaseModel):
    email: str   
    password: str

@app.post("/user-login")
async def user_login(request: Request,logIn: UserLogin):
    value, data = standard_login(logIn.email, logIn.password)
    if value == 1:
        request.session['user'] = logIn.email  # Save user session
        return {"status": "SUCCESS", "data":data }
    return {"status": "FAILED", "data": "unknown error."}

@app.get('/logout')
def logout(request: Request):
    login_method = request.session.get('login_method')
    if login_method == 'google' and 'user' in request.session:
        request.session.pop('user')
    request.session.clear()
    return RedirectResponse(url='/login')

app.include_router(rule_endpoint.router, dependencies=[Depends(get_current_user)])
app.include_router(program.router, dependencies=[Depends(get_current_user)])
app.include_router(user_management.router, dependencies=[Depends(get_current_user)])
app.include_router(validation.router, dependencies=[Depends(get_current_user)])

app.mount("/static", StaticFiles(directory=BUILD_PATH + "/static"), name="static")

@app.get("/program-types")
async def program_types(user=Depends(get_current_user)):
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())

@app.get("/users")
async def users(user=Depends(get_current_user)):
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())

@app.get("/rules")
async def rules(user=Depends(get_current_user)):
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())

@app.get("/validate-content")
async def validate_content(user=Depends(get_current_user)):
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())

@app.get("/validate-video-content")
async def validate_content(user=Depends(get_current_user)):
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())


@app.get("/login")
async def login():
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())

@app.get("/")
async def root(user=Depends(get_current_user)):
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='debug')
