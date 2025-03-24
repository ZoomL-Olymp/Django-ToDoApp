import aiohttp
from bot.config_reader import config
from typing import Dict, Optional, List, Union
import asyncio

BASE_URL = "http://web:8000/api" # Using service name

async def auth_user(telegram_id: int, retries: int = 3, delay: float = 2.0) -> dict | None: # Added retries
    """Авторизация/регистрация пользователя через API."""
    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            try:
                async with session.post(f"{BASE_URL}/telegram-auth/", json={"telegram_id": telegram_id}) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientConnectorError as e:
                print(f"Попытка {attempt + 1}/{retries}. Ошибка подключения к API: {e}")
                if attempt == retries - 1:  # Last attempt
                    return None
                await asyncio.sleep(delay)  # Wait before retrying
            except aiohttp.ClientResponseError as e:
                print(f"Ошибка при запросе к API: {e.status}, message='{e.message}', url='{e.request_info.url}'")
                return None
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
                return None
        
async def get_tasks(access_token: str, retries: int = 3, delay: float = 1.0): # Example for get_tasks
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {access_token}"}
        for attempt in range(retries):
            try:
                async with session.get(f"{BASE_URL}/tasks/", headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientConnectorError as e:
                print(f"Attempt {attempt + 1}/{retries}. Connection error: {e}")
                if attempt == retries - 1:
                    return None
                await asyncio.sleep(delay)
            except aiohttp.ClientResponseError as e:
                print(f"API request error: {e.status}, message='{e.message}', url='{e.request_info.url}'")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None

async def create_task(access_token: str, task_data: dict, retries: int = 3, delay: float = 1.0):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {access_token}"}
        for attempt in range(retries):
            try:
                async with session.post(f"{BASE_URL}/tasks/", headers=headers, json=task_data) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientConnectorError as e:
                print(f"Attempt {attempt+1}/{retries}. Connection Error: {e}")
                if attempt == retries - 1:
                    return None
                await asyncio.sleep(delay)
            except aiohttp.ClientResponseError as e:
                print(f"API request error: {e.status}, message='{e.message}', url='{e.request_info.url}'")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None
async def delete_task_request(access_token: str, task_id: str, retries: int = 3, delay: float = 1.0):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {access_token}"}
        for attempt in range(retries):
            try:
                url = f"{BASE_URL}/tasks/{task_id}/"
                async with session.delete(url, headers=headers) as response:
                    response.raise_for_status()
                    return True  # Или, например, response.status

            except aiohttp.ClientConnectorError as e:
                print(f"Attempt {attempt+1}/{retries}. Connection Error: {e}")
                if attempt == retries - 1:
                    return None
                await asyncio.sleep(delay)

            except aiohttp.ClientResponseError as e:
                print(f"Ошибка при запросе к API (delete): {e.status}, message='{e.message}', url='{e.request_info.url}'")
                return False
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
                return False

async def complete_task(access_token: str, task_id: str, retries: int = 3, delay: float = 1.0):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {access_token}"}
        for attempt in range(retries):
            try:
                url = f"{BASE_URL}/tasks/{task_id}/"
                async with session.patch(url, headers=headers, json={"completed": True}) as response:  # PATCH запрос
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientConnectorError as e:
                print(f"Attempt {attempt+1}/{retries}. Connection Error: {e}")
                if attempt == retries - 1:
                    return None
                await asyncio.sleep(delay)

            except aiohttp.ClientResponseError as e:
                print(f"API request error: {e.status}, message='{e.message}', url='{e.request_info.url}'")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None

async def create_category(access_token: str, category_name: str) -> dict | None:  # Return the created category or None
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with session.post(f"{BASE_URL}/categories/", headers=headers, json={"name": category_name}) as response:
                response.raise_for_status()  # Will raise for 4xx and 5xx errors
                return await response.json()  # Return the JSON response (should contain the new category)
        except aiohttp.ClientConnectorError as e:
            print(f"Connection error: {e}")
            return None
        except aiohttp.ClientResponseError as e:
            print(f"API request error: {e.status}, message='{e.message}', url='{e.request_info.url}'")
            return None  #  Return None on error
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

async def get_categories(access_token: str, retries: int = 3, delay: float = 1.0):  # Add this
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {access_token}"}
        for attempt in range(retries):
            try:
                async with session.get(f"{BASE_URL}/categories/", headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientConnectorError as e:
                print(f"Attempt {attempt + 1}/{retries}. Connection error: {e}")
                if attempt == retries - 1:
                    return None
                await asyncio.sleep(delay)
            except aiohttp.ClientResponseError as e:
                print(f"API request error: {e.status}, message='{e.message}', url='{e.request_info.url}'")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None
        
async def delete_tokens(user_id):
    # Заглушка
    # Нужна реализация удаления токенов на сервере
    print(f"Удаление токенов для пользователя {user_id}")