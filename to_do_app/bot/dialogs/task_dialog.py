from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import Router, F
from bot.states import TaskDialog
from bot.api_client import create_task, get_categories
from bot.utils import UserData
from bot.keyboards import categories_keyboard
from datetime import datetime

router = Router()
@router.message(TaskDialog.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание задачи (или отправьте `-`):")
    await state.set_state(TaskDialog.description)

@router.message(TaskDialog.description)
async def process_description(message: Message, state: FSMContext):
    description = message.text
    if description == "-":
        description = None  # Если пользователь отправил "-", описание будет пустым
    await state.update_data(description=description)
    await message.answer("Введите дату и время выполнения задачи в формате ГГГГ-ММ-ДД ЧЧ:ММ (или отправьте `-`):")
    await state.set_state(TaskDialog.due_date)
@router.message(TaskDialog.due_date)
async def process_due_date(message: Message, state: FSMContext):

    due_date_str = message.text
    if due_date_str == "-":
        await message.answer("Вы не указали дату и время. Укажите категорию")
        await state.set_state(TaskDialog.category)
        return
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
        await state.update_data(due_date=due_date.isoformat())  # Сохраняем в ISO формате
        user_id = message.from_user.id
        access_token, _ = await UserData.get_tokens(user_id)
        categories = await get_categories(access_token) # Получаем список категорий
        if categories:
            # Создаем инлайн-клавиатуру с категориями
            keyboard = categories_keyboard(categories)
            await message.answer("Выберите категорию:", reply_markup=keyboard)
            await state.set_state(TaskDialog.category)  # Переходим к выбору категории
        else:
            await state.update_data(category=None)
            data = await state.get_data()
            access_token, _ = await UserData.get_tokens(message.from_user.id)
            created_task = await create_task(access_token, data)  # Создаем задачу
            if created_task:
                 await message.answer(f"Задача '{created_task['title']}' успешно создана!", reply_markup=ReplyKeyboardRemove())
            else:
                 await message.answer("Не получилось создать задачу", reply_markup=ReplyKeyboardRemove())
            await state.clear()
    except ValueError:
        await message.answer("Неверный формат даты и времени. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД ЧЧ:ММ.")
        return

@router.callback_query(TaskDialog.category, F.data.startswith("category_"))
async def process_category(callback_query: CallbackQuery, state: FSMContext):
    category_id = callback_query.data.split("category_")[1]  # Получаем ID категории из callback_data
    await state.update_data(category=category_id)
    data = await state.get_data()
    access_token, _ = await UserData.get_tokens(callback_query.from_user.id)
    created_task = await create_task(access_token, data) # Создаем задачу в БД

    if created_task:
        await callback_query.message.answer(f"Задача '{created_task['title']}' успешно создана!")
    else:
        await callback_query.message.answer("Не получилось создать задачу")
    await state.clear()  # Очищаем состояние
    await callback_query.answer()

async def add_task_handler(message: Message, state: FSMContext):
    await message.answer("Введите название задачи:")
    await state.set_state(TaskDialog.title)