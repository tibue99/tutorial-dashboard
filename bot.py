import discord
import ezcord
from discord.ext.ipc import Server


class Bot(ezcord.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.ipc = Server(self, secret_key="keks")

    async def on_ready(self):
        await self.ipc.start()
        print(f"{self.user} ist online")

    @Server.route()
    async def guild_count(self, _):
        return str(len(self.guilds))

    async def on_ipc_error(self, endpoint: str, exc: Exception):
        raise exc


bot = Bot()
bot.run("TOKEN")  # Hier den Bot-Token einfügen
