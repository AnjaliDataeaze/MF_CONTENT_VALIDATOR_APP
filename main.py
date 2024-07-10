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

# oauth = OAuth()
# oauth.register(
#     name='google',
#     server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
#     client_id=GOOGLE_CLIENT_ID,
#     client_secret=GOOGLE_CLIENT_SECRET,
#     client_kwargs={
#         'scope': 'email openid profile',
#         'redirect_url': REDIRECT_URL
#     }
# )

# def get_current_user(request: Request):
#    return  request.session.get('user')
    


# def get_current_user(request: Request):
#     user = request.session.get('user')
    
#     if user !=1 :
#         return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
#     return user

'''
def get_current_user(request: Request):
    user = request.session.get('user')
    print("CURRENT_USER--->", user)
    if not user:
        print("######################")
        print("User Not Found")
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user
'''

# @app.get("/home")
# def index(request: Request):
#     user = request.session.get('user')
#     if user is not None:
#         return HTMLResponse("<p>You are already logged in. <a href='/logout'>Logout</a></p>")
#     else:
#         html = """
#         <h1>Welcome to the Login Page</h1>
#         <a href='/google-login'>Login with Google</a><br>
#         <a href='/standard-login-form'>Login with Username and Password</a>
#         """
#         return HTMLResponse(html)

# @app.get("/standard-login-form")
# def standard_login_form(request: Request):
#     html = """
#     <h1>Standard Login</h1>
#     <form action="/user-login" method="post">
#         <label for="email">Email:</label>
#         <input type="email" id="email" name="email" required><br><br>
#         <label for="password">Password:</label>
#         <input type="password" id="password" name="password" required><br><br>
#         <button type="submit">Login</button>
#     </form>
#     """
#     return HTMLResponse(html)

'''
@app.get("/google-login")
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)

@app.get('/auth')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
        request.session['login_method'] = 'google'  # Storing the login method
    return RedirectResponse(url='/root')

# @app.get('/google-logout')
# def logout(request: Request):
#     if 'user' in request.session:
#         request.session.pop('user')
#         request.session.clear()
#     else:
#         request.session.clear()
#     return RedirectResponse(url='/home')
'''

# class UserLogin(BaseModel):
#     email: str
#     password: str

# @app.post("/user-login")
# async def userlogin(request: Request, logIn: UserLogin):
#     print("Calling Standard login")
#     user = standard_login(logIn.email, logIn.password)
#     print("USER", user)
#     if user==1:
#         request.session['user'] = user
#         request.session['login_method'] = 'standard'
#         print("Request_Session_of_Login", request.session)
#         return RedirectResponse(url='/root', status_code=303)
#     elif user == 3:
#         raise HTTPException(status_code=401, detail="User Not FOund")
#     else:
#         raise HTTPException(status_code=401, detail="Incorrect username or password")

# @app.post("/user-login")
# async def userlogin(logIn: UserLogin):
#     print("Calling Standard login")
#     value = standard_login(logIn.email, logIn.password)
#     print("USER", value)
#     return {"status": "SUCCESS" if value == 1 else "FAILED", "data": "unknown error."}

# @app.post("/user-login")
# async def userlogin(logIn: UserLogin):
   
#     user = standard_login(logIn.email, logIn.password)
    
#     if user==1:
#         return RedirectResponse(url='/root', status_code=303)
#     elif user == 3:
#         raise HTTPException(status_code=401, detail="User Not FOund")
#     else:
#         raise HTTPException(status_code=401, detail="Incorrect username or password")


# @app.get('/logout')
# def logout(request: Request):
#     login_method = request.session.get('login_method')
#     print("login_method-->",login_method)
#     print("Request_Session_of_Login", request.session)
#     if login_method == 'google':
#         if 'user' in request.session:
#             request.session.pop('user')
#             request.session.clear()
#         else:
#             request.session.clear()
#         return RedirectResponse(url='/login')

#     request.session.pop('user', None)  # Remove user data from session
#     request.session.clear()            # Clear all other session data
#     return RedirectResponse(url='/login')

app.include_router(rule_endpoint.router)
app.include_router(program.router)
app.include_router(user_management.router)
app.include_router(validation.router)


app.mount("/static", StaticFiles(directory= BUILD_PATH + "/static"), name="static")

# @app.get("/programtypes")
# async def program_types(request: Request, user=Depends(get_current_user)):
#     if user == 1:
#         return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())
#     else:
#         return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)


@app.get("/programtypes")
async def program_types():
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())

@app.get("/users")
async def users():
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())
   
@app.get("/rules")
async def rule_endpoint():
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())

@app.get("/validate-content")
async def validate_content():
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())

@app.get("/root")
async def root():
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())

@app.get("/login")
async def login():
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())


# @app.get("/users")
# async def users(request: Request, user=Depends(get_current_user)):
#     if user == 1:
#         return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())
#     else:
#         return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)

 


# @app.get("/programtypes")
# async def program_types(request: Request):
#     try:
#         user = get_current_user(request)
#     except HTTPException as e:
#         print("E-Status code--->",e.status_code)
#         if e.status_code == 401:
#             print("*************************************")
#             return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
#         else:
#             raise e
#     return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())




# @app.get("/rules")
# async def rule_endpoint(request: Request, user=Depends(get_current_user)):
#     return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())


# @app.get("/validate-content")
# async def validate_content(request: Request, user=Depends(get_current_user)):
#     return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())


# @app.get("/root")
# async def root(request: Request, user=Depends(get_current_user)):
#     return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())





if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='debug')

