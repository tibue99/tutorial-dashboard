# Discord Bot Dashboard Tutorial
Hier findest du den Code zum Dashboard Tutorial. Für dieses Tutorial benutzen wir [FastAPI](https://fastapi.tiangolo.com/).

## Infos
Das Dashboard kann mit einer beliebigen Discord-Library verwendet werden 
   ([Pycord](https://github.com/Pycord-Development/pycord),
   [Discord.py](https://github.com/Rapptz/discord.py),
   [Nextcord](https://github.com/nextcord/nextcord),
   ...)

1. Nachdem du eine Discord Library installiert hast, installiere alle Packages aus `requirements.txt`
   ```
   pip install -r requirements.txt
   ```
2. Füge einen Redirect im [Discord Developer Portal](https://discord.com/developers/applications) hinzu
   ```
   http://localhost:8000/callback
   ```
3. Aktiviere den **Member Intent** im Developer Portal
4. Füge die Daten aus dem Developer Portal in `main.py` ein
5. Starte die Dashboard-API in `main.py` und den Bot in `bot.py`
   