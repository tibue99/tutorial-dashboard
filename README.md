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

## VPS Hosting
Das Dashboard kann zum Beispiel auf einem VPS gehostet werden. Hier ist eine kleine Übersicht für Ubuntu.

**Wichtig:** Nicht vergessen den Redirect im Dev Portal und im Code anzupassen.
Dort steht dann nicht mehr `localhost`, sondern eure IP-Adresse oder eure Domain.

Folgende Befehle werden auf dem VPS ausgeführt:
1. Packages aktualisieren: `apt update`
2. Pip und Tmux installieren: `apt install python3-pip tmux`
3. Requirements installieren: `pip install -r requirements.txt`
4. `bot.py` und `main.py` jeweils in einer eigenen Tmux-Session starten
5. Nginx-Konfiguration anpassen: `/etc/nginx/sites-available/`
   ```nginx
   server {
      listen 80;
      server_name _;  # IP-Adresse oder Domain eintragen

      location / {
         proxy_pass http://127.0.0.1:8000;
         include /etc/nginx/proxy_params;
         proxy_redirect off;
      }

      location /static {
         alias /home/dashboard/frontend/static;
      }
   }
   ```
6. Nginx neustarten: `sudo systemctl restart nginx`
