import aiohttp
from bot.config_reader import config
from typing import Dict, Optional, List, Union
BASE_URL = "http://localhost:8000/api"

async def auth_user(telegram_id: int) -> dict | None: # Возвращает словарь с токенами или None
    """Авторизация/регистрация пользователя через API."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("http://localhost:8000/api/telegram-auth/", json={"telegram_id": str(telegram_id)}) as response: # json
                response.raise_for_status()  # Проверяем статус ответа (200 OK)
                return await response.json()  # Возвращаем токены
        except aiohttp.ClientError as e:
            print(f"Ошибка при запросе к API: {e}")
            return None

async def delete_tokens(user_id):
    # Заглушка
    # Нужна реализация удаления токенов на сервере
    print(f"Удаление токенов для пользователя {user_id}")

async def get_tasks(access_token: str): # Получение списка задач
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with session.get("http://localhost:8000/api/tasks/", headers=headers) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Ошибка при запросе к API: {e}")
            return None
async def create_task(access_token: str, task_data: dict): # Создание задачи
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with session.post("http://localhost:8000/api/tasks/", headers=headers, json=task_data) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Ошибка при запросе к API {e}")

async def delete_task_request(access_token: str, task_id: str): # Удаление задачи
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            url = f"http://localhost:8000/api/tasks/{task_id}/"
            async with session.delete(url, headers=headers) as response:
                response.raise_for_status()
                return True  # Или, например, response.status
        except aiohttp.ClientError as e:
            print(f"Ошибка при запросе к API (delete): {e}")
            return False
async def complete_task(access_token: str, task_id: str): # Завершение задачи
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            url = f"http://localhost:8000/api/tasks/{task_id}/"
            async with session.patch(url, headers=headers, json={"completed": True}) as response: # PATCH запрос
                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as e:
            print(f"API request error: {e}")
            return None
async def get_categories(access_token: str): # Получение списка категорий
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with session.get("http://localhost:8000/api/categories/", headers=headers) as response:
                response.raise_for_status()  # Проверяем статус ответа (200 OK)
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Ошибка при запросе к API: {e}")
            return None