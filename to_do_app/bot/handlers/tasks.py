from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards import main_keyboard
from bot.api_client import get_tasks, delete_task_request, complete_task, create_task, get_categories
from bot.utils import UserData
from bot.dialogs.task_dialog import TaskDialog, add_task_handler
from datetime import datetime
from bot.keyboards import categories_keyboard

router = Router()

class DeleteTask(StatesGroup):
    waiting_for_id = State()

class CompleteTask(StatesGroup):
    waiting_for_id = State()

@router.message(F.text == "/list")
async def list_tasks(message: Message):
    user_id = message.from_user.id
    access_token, refresh_token = await UserData.get_tokens(user_id)
    if not access_token:
        await message.answer("Вы не авторизованы. Используйте /start")
        return

    tasks = await get_tasks(access_token)
    if tasks is not None:
        if tasks:
            response_text = "Ваши задачи:\n"
            for task in tasks:
                status = "Выполнено" if task['completed'] else "Не выполнено"
                category_name = "Без категории"  # Default if no category
                if task["category"]:
                    categories = await get_categories(access_token)
                    if categories: # Added check for empty
                        for cat in categories:
                            if cat["id"] == task["category"]:
                                category_name = cat["name"]
                                break  # Exit inner loop once found
                response_text += (
                    f"\nID: {task['user_task_id']}\n"  # Display user_task_id
                    f"Название: {task['title']}\n"
                    f"Описание: {task['description']}\n"
                    f"Срок: {task['due_date']}\n"
                    f"Категория: {category_name}\n"  # Display category name
                    f"Статус: {status}\n"
                )
            await message.answer(response_text, reply_markup=main_keyboard)
        else:
            await message.answer("У вас пока нет задач.", reply_markup=main_keyboard)
    else:
        await message.answer("Ошибка при получении списка задач.")

@router.message(F.text == "/add")
async def add_task(message: Message, state: FSMContext):
    await message.answer("Введите название задачи:")
    await state.set_state(TaskDialog.title)


@router.message(F.text == "/delete")
async def delete_task(message: Message, state: FSMContext):
    user_id = message.from_user.id
    access_token, _ = await UserData.get_tokens(user_id)
    if not access_token:
        await message.answer("Вы не авторизованы. Используйте /start")
        return
    await message.answer("Введите ID задачи, которую хотите удалить:")
    await state.set_state(DeleteTask.waiting_for_id)

@router.message(DeleteTask.waiting_for_id)
async def process_task_id_for_deletion(message: Message, state: FSMContext):
    user_id = message.from_user.id
    access_token, _ = await UserData.get_tokens(user_id)
    if not access_token:
        await message.answer("Вы не авторизованы")
        return

    try:
        user_task_id = int(message.text)
    except ValueError:
        await message.answer("Неверный ID задачи. Пожалуйста, введите число.")
        await state.set_state(DeleteTask.waiting_for_id) # Stay in the same state
        return

    tasks = await get_tasks(access_token)  # Get all tasks for the user
    if tasks is None:
        await message.answer("Ошибка при получении списка задач.")
        await state.clear()
        return

    task_to_delete = None
    for task in tasks:
        if task['user_task_id'] == user_task_id:
            task_to_delete = task
            break

    if task_to_delete is None:
        await message.answer("Задача с таким ID не найдена.")
        await state.clear()
        return

    success = await delete_task_request(access_token, task_to_delete['id'])  # Use the API
    await state.clear()
    if success:
        await message.answer(f"Задача с ID {user_task_id} удалена.", reply_markup=main_keyboard) # Add keyboard
    else:
        await message.answer(f"Не удалось удалить задачу с ID {user_task_id}. Проверьте ID и попробуйте снова.", reply_markup=main_keyboard) # Add keyboard


@router.message(F.text == "/done")
async def done_task(message: Message, state: FSMContext):
    user_id = message.from_user.id
    access_token, _ = await UserData.get_tokens(user_id)
    if not access_token:
        await message.answer("Вы не авторизованы. Используйте /start")
        return
    await message.answer("Введите ID задачи, которую хотите отметить выполненной:")
    await state.set_state(CompleteTask.waiting_for_id)


@router.message(CompleteTask.waiting_for_id)
async def process_task_id_for_complete(message: Message, state: FSMContext):
    user_id = message.from_user.id
    access_token, _ = await UserData.get_tokens(user_id)
    if not access_token:
        await message.answer("Вы не авторизованы")
        return

    try:
        user_task_id = int(message.text)
    except ValueError:
        await message.answer("Неверный ID задачи.  Пожалуйста, введите число.")
        await state.set_state(CompleteTask.waiting_for_id)
        return
    tasks = await get_tasks(access_token)  # Get all tasks for the user
    if tasks is None:
        await message.answer("Ошибка при получении списка задач.")
        await state.clear()
        return

    task_to_complete = None
    for task in tasks:
        if task['user_task_id'] == user_task_id:
            task_to_complete = task
            break

    if task_to_complete is None:
        await message.answer("Задача с таким ID не найдена.")
        await state.clear()
        return

    updated_task = await complete_task(access_token, task_to_complete['id'])  # Use the API
    await state.clear()

    if updated_task:
        await message.answer(f"Задача с ID '{user_task_id}' отмечена как выполненная", reply_markup=main_keyboard) # Add keyboard
    else:
        await message.answer(f"Не удалось задачу с ID {user_task_id}. Проверьте ID", reply_markup=main_keyboard) # Add keyboard

@router.callback_query(TaskDialog.category, F.data.startswith("category_"))
async def process_category(callback_query: CallbackQuery, state: FSMContext):
    category_id = callback_query.data.split("category_")[1]

    await state.update_data(category=category_id)
    data = await state.get_data()
    access_token, _ = await UserData.get_tokens(callback_query.from_user.id)
    created_task = await create_task(access_token, data)

    if created_task:
        await callback_query.message.answer(f"Задача '{created_task['title']}' успешно создана!", reply_markup=main_keyboard)
    else:
        await callback_query.message.answer("Не получилось создать задачу", reply_markup=main_keyboard)
    await state.clear()
    await callback_query.answer()

@router.message(TaskDialog.due_date)
async def process_due_date(message: Message, state: FSMContext):
    due_date_str = message.text
    if due_date_str == "-":
        await message.answer("Вы не указали дату и время. Укажите категорию")
        await state.set_state(TaskDialog.category)
        return
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer("Неверный формат даты и времени. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД ЧЧ:ММ.")
        return

    await state.update_data(due_date=due_date.isoformat())

    user_id = message.from_user.id
    access_token, _ = await UserData.get_tokens(user_id)
    categories = await get_categories(access_token)

    if categories:
        keyboard = categories_keyboard(categories)
        await message.answer("Выберите категорию:", reply_markup=keyboard)
        await state.set_state(TaskDialog.category)
    else:
        await state.update_data(category=None)
        data = await state.get_data()
        access_token, _ = await UserData.get_tokens(message.from_user.id)
        created_task = await create_task(access_token, data)
        if created_task:
            await message.answer(f"Задача '{created_task['title']}' успешно создана!", reply_markup=main_keyboard) # Use main_keyboard
        else:
            await message.answer("Не получилось создать задачу.", reply_markup=main_keyboard) # Use main_keyboard
        await state.clear()