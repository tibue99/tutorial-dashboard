import uvicorn
from discord.ext.ipc import Client
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from backend import api

# Hier die Daten aus dem Developer-Portal einfügen
CLIENT_ID = 123456789
CLIENT_SECRET = ""
REDIRECT_URI = "http://localhost:8000/callback"
LOGIN_URL = ""


app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend")

ipc = Client(secret_key="keks")


@app.get("/")
async def home(request: Request):
    guild_count = await ipc.request("guild_count")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "count": guild_count.response,
            "login_url": LOGIN_URL
        },
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

    return RedirectResponse(url="/guilds")


@app.get("/guilds")
async def guilds():
    return {"success": "Erfolgreich eingeloggt"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
    # uvicorn.run("main:app", host="localhost", port=8000, reload=True)
