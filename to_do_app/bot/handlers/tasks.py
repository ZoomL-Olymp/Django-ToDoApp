from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards import main_keyboard
from bot.api_client import get_tasks, delete_task_request, complete_task, create_task, get_categories # Import create_task
from bot.utils import UserData
from bot.dialogs.task_dialog import TaskDialog, add_task_handler # Import dialog
from datetime import datetime
from bot.keyboards import categories_keyboard # Import inline

router = Router()

# States for deleting a task
class DeleteTask(StatesGroup):
    waiting_for_id = State()

# States for completing a task
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
                response_text += (
                    f"\nID: {task['user_task_id']}\n"  # Display user_task_id
                    f"Название: {task['title']}\n"
                    f"Описание: {task['description']}\n"
                    f"Срок: {task['due_date']}\n"
                    f"Категория: {task['category']}\n" # Add category
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

    try:
        # Use afirst() to get the first result or None
        task = await Task.objects.filter(user=user_id, user_task_id=user_task_id).afirst()
        if not task:
            await message.answer("Задача с таким ID не найдена.")
            await state.clear()
            return
        task_id = task.id # Get real id

    except Exception as e: # Added exception
        print(f"Database error: {e}") # For debug
        await message.answer("Ошибка при работе с базой данных.")
        await state.clear()
        return

    success = await delete_task_request(access_token, task_id) # Use real id
    await state.clear()
    if success:
        await message.answer(f"Задача с ID {user_task_id} удалена.")
    else:
        await message.answer(f"Не удалось удалить задачу с ID {user_task_id}. Проверьте ID и попробуйте снова.")

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
        await state.set_state(CompleteTask.waiting_for_id) # Stay in same state
        return

    try:
        task = await Task.objects.filter(user=user_id, user_task_id=user_task_id).afirst() # Use afirst()
        if not task: # Check with task is None
            await message.answer("Задача с таким ID не найдена.")
            await state.clear() # Clear state
            return
        task_id = task.id # Get real id

    except Exception as e:  # Added exception
        print(f"Database error: {e}")  # For debug
        await message.answer("Ошибка при работе с базой данных.")
        await state.clear()
        return

    updated_task = await complete_task(access_token, task_id)  # Pass correct id to complete_task
    await state.clear()

    if updated_task:
        await message.answer(f"Задача с ID '{user_task_id}' отмечена как выполненная") # Show user id
    else:
        await message.answer(f"Не удалось задачу с ID {user_task_id}. Проверьте ID")