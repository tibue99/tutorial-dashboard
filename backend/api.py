import aiohttp

API_ENDPOINT = "https://discord.com/api"


async def get_token_response(data):
    async with aiohttp.ClientSession() as session:
        response = await session.post(API_ENDPOINT + "/oauth2/token", data=data)
        json_response = await response.json()

    access_token = json_response.get("access_token")
    refresh_token = json_response.get("refresh_token")
    expires_in = json_response.get("expires_in")

    if not access_token or not refresh_token:
        return None

    return access_token, refresh_token, expires_in
