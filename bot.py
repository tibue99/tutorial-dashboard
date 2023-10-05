import discord
import ezcord
from discord.ext.ipc import Server, ClientPayload


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

    @Server.route()
    async def guild_stats(self, data: ClientPayload):
        guild = self.get_guild(data.guild_id)
        if not guild:
            return {
                "member_count": 69,
                "name": "Unbekannt"
            }

        return {
            "member_count": guild.member_count,
            "name": guild.name,
        }

    async def on_ipc_error(self, endpoint: str, exc: Exception) -> None:
        raise exc


bot = Bot()
bot.run("TOKEN")  # Hier den Bot-Token einfügen
