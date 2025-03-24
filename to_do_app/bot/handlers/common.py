from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply import main_keyboard #  WIP | placeholder
from api_client import auth_user, delete_tokens #  WIP | placeholder
from utils import UserData  #  WIP | placeholder

async def command_start(message: Message):
    user_id = message.from_user.id
    access_token, refresh_token = await UserData.get_tokens(user_id)
    if access_token: # Если уже авторизован
        await message.answer("Вы уже авторизованы!", reply_markup=main_keyboard)
        return
    
    tokens = await auth_user(user_id) # Авторизуемся через API
    if tokens:
        await UserData.save_tokens(user_id, tokens['access'], tokens['refresh'])
        await message.answer("Вы успешно авторизованы!", reply_markup=main_keyboard)
    else:
        await message.answer("Ошибка авторизации.")

async def command_help(message: Message):
    help_text = """
Доступные команды:
/start - Начать работу с ботом
/list - Список задач
/add - Добавить задачу
/done - Отметить задачу выполненной
/delete - Удалить задачу
/categories - Список категорий
/help - Помощь
    """
    await message.answer(help_text)