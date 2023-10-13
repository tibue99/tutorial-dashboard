import aiohttp

API_ENDPOINT = "https://discord.com/api"


class DiscordAuth:
    client_id: str
    client_secret: str
    redirect_uri: str
    session: aiohttp.ClientSession | None

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        self.auth = aiohttp.BasicAuth(str(client_id), client_secret)

    async def setup(self):
        self.session = aiohttp.ClientSession()

    async def get_user(self, token):
        headers = {"Authorization": f"Bearer {token}"}
        async with self.session.get(API_ENDPOINT + "/users/@me", headers=headers) as response:
            return await response.json()

    async def get_guilds(self, token):
        headers = {"Authorization": f"Bearer {token}"}
        async with self.session.get(API_ENDPOINT + "/users/@me/guilds", headers=headers) as response:
            return await response.json()

    async def get_token_response(self, data):
        response = await self.session.post(API_ENDPOINT + "/oauth2/token", data=data)
        json_response = await response.json()

        access_token = json_response.get("access_token")
        refresh_token = json_response.get("refresh_token")
        expires_in = json_response.get("expires_in")

        if not access_token or not refresh_token:
            return None

        return access_token, refresh_token, expires_in

    async def revoke_token(self, token):
        async with self.session.post(
                API_ENDPOINT + "/oauth2/token/revoke",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={"token": token},
                auth=self.auth
        ) as response:
            response.raise_for_status()
