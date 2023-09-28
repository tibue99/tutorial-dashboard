import uvicorn
from discord.ext.ipc import Client
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from backend import DiscordAuth, db


# Hier die Daten aus dem Developer-Portal einfügen
CLIENT_ID = 123456789
CLIENT_SECRET = ""
REDIRECT_URI = "http://localhost:8000/callback"
LOGIN_URL = ""


app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend")

ipc = Client(secret_key="keks")
api = DiscordAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)


@app.on_event("startup")
async def on_startup():
    await api.setup()
    await db.setup()


@app.get("/")
async def home(request: Request):
    guild_count = await ipc.request("guild_count")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "count": guild_count.response,
            "login_url": LOGIN_URL
        }
    )


@app.get("/callback")
async def callback(code: str):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    result = await api.get_token_response(data)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid Auth Code")

    token, refresh_token, expires_in = result
    user = await api.get_user(token)
    user_id = user.get("id")

    session_id = await db.add_session(token, refresh_token, expires_in, user_id)

    response = RedirectResponse(url="/guilds")
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response


@app.get("/guilds")
async def guilds(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="no auth")

    session = await db.get_session(session_id)
    token, refresh_token, token_expires_at, user_id = session

    user = await api.get_user(token)
    user_guilds = await api.get_guilds(token)

    return templates.TemplateResponse(
        "guilds.html",
        {
            "request": request,
            "global_name": user["global_name"],
            "guilds": user_guilds
        }
    )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
    # uvicorn.run("main:app", host="localhost", port=8000, reload=True)
