from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from src.config.credentials import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URL
from src.endpoints import program, validation, user_management
from src.endpoints import rule_endpoint



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




def get_current_user(request: Request):
    '''
    Functinality to access user from session, it will ensure 
    that user need to be in session to access apis
    ''' 
    user = request.session.get('user')
    if not user:
        # return RedirectResponse(url='/home')
    
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user

@app.get("/home")
def index(request: Request):
    user = request.session.get('user')

    if user is not None:
        email = user['email']
        html = (
            f'<pre>Email: {email}</pre><br>'
            '<a href="/login">login</a>'
        )
        return HTMLResponse(html)

    # Show the login link
    return HTMLResponse('<a href="/login">login</a>')

@app.get("/login")
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)

@app.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)       
    except OAuthError as e:
        return HTMLResponse(content=str(e))
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/root')

@app.get('/logout')
def logout(request: Request):
    if 'user' in request.session:
        request.session.pop('user')
        request.session.clear()
    else:
        request.session.clear()
    return RedirectResponse(url='/home')


app.include_router(rule_endpoint.router)
app.include_router(program.router)
app.include_router(user_management.router)
app.include_router(validation.router)


app.mount("/static", StaticFiles(directory="/home/user/Downloads/build/static"), name="static")

@app.get("/programtypes")
async def program_types(request: Request, user=Depends(get_current_user)):
    return HTMLResponse(content=open("/home/user/Downloads/build/index.html").read())

@app.get("/rules")
async def rule_endpoint(request: Request, user=Depends(get_current_user)):
    return HTMLResponse(content=open("/home/user/Downloads/build/index.html").read())

@app.get("/validate-content")
async def validate_content(request: Request, user=Depends(get_current_user)):
    return HTMLResponse(content=open("/home/user/Downloads/build/index.html").read())

@app.get("/root")
async def root(request: Request, user=Depends(get_current_user)):
    return HTMLResponse(content=open("/home/user/Downloads/build/index.html").read())

    




if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='debug')




