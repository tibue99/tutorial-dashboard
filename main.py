from datetime import datetime

import discord
import uvicorn
from discord.ext.ipc import Client
from fastapi import FastAPI, Request, HTTPException, Cookie
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from backend import DiscordAuth, db


# Hier die Daten aus dem Developer-Portal einfügen
CLIENT_ID = 123456789
CLIENT_SECRET = ""
REDIRECT_URI = "http://localhost:8000/callback"
LOGIN_URL = ""
INVITE_LINK = ""


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
    session_id = request.cookies.get("session_id")
    if session_id and await db.get_session(session_id):
        return RedirectResponse(url="/guilds")

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
    session = await db.get_session(session_id)
    if not session_id or not session:
        raise HTTPException(status_code=401, detail="no auth")

    token, refresh_token, token_expires_at = session

    user = await api.get_user(token)
    if datetime.now() > token_expires_at or user.get("code") == 0:
        if await api.reload(session_id, refresh_token):
            RedirectResponse(url="/guilds")
        else:
            RedirectResponse(url="/logout")

    if "id" not in user:
        return RedirectResponse(url="/logout")

    user_guilds = await api.get_guilds(token)
    bot_guilds = await ipc.request("bot_guilds")
    perms = []

    for guild in user_guilds:
        if guild["id"] in bot_guilds.response["data"]:
            guild["url"] = "/server/" + str(guild["id"])
        else:
            guild["url"] = INVITE_LINK + f"&guild_id={guild['id']}"

        if guild["icon"]:
            guild["icon"] = "https://cdn.discordapp.com/icons/" + guild["id"] + "/" + guild["icon"]
        else:
            guild["icon"] = "https://cdn.discordapp.com/embed/avatars/0.png"

        is_admin = discord.Permissions(int(guild["permissions"])).administrator
        if is_admin or guild["owner"]:
            perms.append(guild)

    return templates.TemplateResponse(
        "guilds.html",
        {
            "request": request,
            "global_name": user["global_name"],
            "guilds": perms
        }
    )


@app.get("/server/{guild_id}")
async def server(request: Request, guild_id: int):
    session_id = request.cookies.get("session_id")
    if not session_id or not await db.get_session(session_id):
        raise HTTPException(status_code=401, detail="no auth")

    stats = await ipc.request("guild_stats", guild_id=guild_id)
    return templates.TemplateResponse(
        "server.html",
        {
            "request": request,
            "name": stats.response["name"],
            "count": stats.response["member_count"],
            "id": guild_id,
        }
    )


@app.get("/logout")
async def logout(session_id: str = Cookie(None)):
    session = await db.get_session(session_id)
    if not session_id or not session:
        raise HTTPException(status_code=401, detail="no auth")

    token, _, _ = session

    response = RedirectResponse("/")
    response.delete_cookie(key="session_id", httponly=True)

    await db.delete_session(session_id)
    await api.revoke_token(token)

    return response


@app.exception_handler(404)
async def error_redirect(_, __):
    return RedirectResponse("/")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
    # uvicorn.run("main:app", host="localhost", port=8000, reload=True)
