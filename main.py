from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_401_UNAUTHORIZED,HTTP_302_FOUND

from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles

from src.config.credentials import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URL, BUILD_PATH
from src.endpoints import program, validation, user_management, rule_endpoint
from src.mf_user_management import standard_login
from fastapi import Form, HTTPException 
from pydantic import BaseModel


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="add any string...")

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_url': REDIRECT_URL
    }
)

# def get_current_user(request: Request):
#     user = request.session.get('user')
#     if not user:
#         return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
#     return user

def get_current_user(request: Request):
   return  request.session.get('user')
    

'''
@app.get("/home")
def index(request: Request):
    user = request.session.get('user')
    if user is not None:
        return HTMLResponse("<p>You are already logged in. <a href='/logout'>Logout</a></p>")
    else:
        html = """
        <h1>Welcome to the Login Page</h1>
        <a href='/google-login'>Login with Google</a><br>
        <a href='/standard-login-form'>Login with Username and Password</a>
        """
        return HTMLResponse(html)

@app.get("/standard-login-form")
def standard_login_form(request: Request):
    html = """
    <h1>Standard Login</h1>
    <form action="/user-login" method="post">
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required><br><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required><br><br>
        <button type="submit">Login</button>
    </form>
    """
    return HTMLResponse(html)

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



class UserLogin(BaseModel):
    email: str
    password: str


@app.post("/user-login")
async def login(request: Request, logIn: UserLogin):
    print("USER_LOGIN")
    print("Email",logIn.email)
    user = standard_login(logIn.email, logIn.password)
    if user==1:
        request.session['user'] = user
        request.session['login_method'] = 'standard'
        print("Request_Session_of_Login", request.session)
        return RedirectResponse(url='/root', status_code=303)
    elif user == 3:
        raise HTTPException(status_code=401, detail="User Not FOund")
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")


@app.get('/logout')
def logout(request: Request):
    login_method = request.session.get('login_method')
    if login_method == 'google':
        if 'user' in request.session:
            request.session.pop('user')
            request.session.clear()
        else:
            request.session.clear()
        return RedirectResponse(url='/login')

    request.session.pop('user', None)  # Remove user data from session
    request.session.clear()            # Clear all other session data
    return RedirectResponse(url='/login')

@app.get('/login')
async def login(request: Request, logIn: UserLogin):
    raise HTTPException(status_code=401, detail="User Not FOund")
    
user = get_current_user(request=Request)

app.include_router(rule_endpoint.router)
app.include_router(program.router)
app.include_router(user_management.router)
app.include_router(validation.router)


app.mount("/static", StaticFiles(directory= BUILD_PATH + "/static"), name="static")


@app.get("/programtypes")
async def program_types(request: Request, user=Depends(get_current_user)):
    if user ==1:
        return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())
    else:
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)



@app.get("/rules")
async def rule_endpoint(request: Request, user=Depends(get_current_user)):
    if user ==1:
       return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())
    else:
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)



@app.get("/validate-content")
async def validate_content(request: Request, user=Depends(get_current_user)):
    if user == 1:
        return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())
    else:
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)


@app.get("/root")
async def root(request: Request, user=Depends(get_current_user)):
    if user ==1:
        return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())
    else:
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)



@app.get("/login")
async def login():
    return HTMLResponse(content=open(BUILD_PATH+"/index.html").read())

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='debug')


