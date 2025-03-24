# bot/api_client.py
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

DJANGO_API_URL = os.getenv("DJANGO_API_URL")

class APIClient:
    def __init__(self):
        self.base_url = DJANGO_API_URL

    async def _make_request(self, method, endpoint, data=None, params=None, headers=None):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}{endpoint}"
            async with session.request(method, url, json=data, params=params, headers=headers) as response:
                if response.status == 204:  # No Content
                    return None
                return await response.json()


    ### Здесь остальные методы