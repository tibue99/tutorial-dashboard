import discord
import ezcord
from discord.ext.ipc import Server, ClientPayload


class Bot(ezcord.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True

        super().__init__(intents=intents)
        self.ipc = Server(self, secret_key="keks")

    async def on_ready(self):
        await self.ipc.start()
        print(f"{self.user} ist online")

    @Server.route()
    async def guild_count(self, _):
        return str(len(self.guilds))

    @Server.route()
    async def bot_guilds(self, _):
        guild_ids = [str(guild.id) for guild in self.guilds]
        return {"data": guild_ids}

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

    @Server.route()
    async def check_perms(self, data: ClientPayload):
        guild = self.get_guild(data.guild_id)
        if not guild:
            return {"perms": False}

        member = guild.get_member(int(data.user_id))
        if not member or not member.guild_permissions.administrator:
            return {"perms": False}

        return {"perms": True}

    async def on_ipc_error(self, endpoint: str, exc: Exception) -> None:
        raise exc


bot = Bot()
bot.run("TOKEN")  # Hier den Bot-Token einfügen
