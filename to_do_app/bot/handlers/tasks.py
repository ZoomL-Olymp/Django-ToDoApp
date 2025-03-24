from aiogram import Router, F
from aiogram.types import Message
from bot.keyboards import main_keyboard
from bot.api_client import get_tasks, delete_task_request, complete_task
from bot.utils import UserData  # WIP | placeholder
from aiogram.fsm.context import FSMContext
from bot.dialogs.task_dialog import TaskDialog, add_task_handler
async def list_tasks(message: Message):
    user_id = message.from_user.id
    access_token, refresh_token = await UserData.get_tokens(user_id)
    if not access_token:
        await message.answer("Вы не авторизованы. Используйте /start")
        return

    tasks = await get_tasks(access_token) # Получаем список задач с API
    if tasks is not None:
        if tasks:
            response_text = "Ваши задачи:\n"
            for task in tasks:
                status = "Выполнено" if task['completed'] else "Не выполнено"
                response_text += (
                    f"\nID: {task['id']}\n"
                    f"Название: {task['title']}\n"
                    f"Описание: {task['description']}\n"
                    f"Срок: {task['due_date']}\n"
                    f"Статус: {status}\n"

                )
            await message.answer(response_text, reply_markup=main_keyboard)
        else:
            await message.answer("У вас пока нет задач.", reply_markup=main_keyboard)
    else:
        await message.answer("Ошибка при получении списка задач.")
async def add_task(message: Message, state: FSMContext):
    await message.answer("Введите название задачи:")
    await state.set_state(TaskDialog.title)

async def delete_task(message: Message): # Пока что через ID, сменить на название потом
    user_id = message.from_user.id
    access_token, _ = await UserData.get_tokens(user_id)
    if not access_token:
        await message.answer("Вы не авторизованы. Используйте /start")
        return
    await message.answer("Введите ID задачи, которую хотите удалить:")

    @Router().message(F.text) # Вложенный обработчик вынести в отдельный handler
    async def process_task_id_for_deletion(inner_message: Message): # inner_message, потому что message занят
        task_id = inner_message.text
        success = await delete_task_request(access_token, task_id)
        if success:
            await inner_message.answer(f"Задача с ID {task_id} удалена.")
        else:
            await inner_message.answer(f"Не удалось удалить задачу с ID {task_id}. Проверьте ID и попробуйте снова.")

async def done_task(message: Message): # Пока что через ID, сменить на название потом
    user_id = message.from_user.id
    access_token, _ = await UserData.get_tokens(user_id)

    if not access_token:
        await message.answer("Вы не авторизованы. Используйте /start")
        return
    await message.answer("Введите ID задачи, которую хотите отметить выполненной:")

    @Router().message(F.text) # Вложенный обработчик вынести в отдельный handler
    async def process_task_id_for_complete(inner_message: Message):
        task_id = inner_message.text
        updated_task = await complete_task(access_token, task_id)

        if updated_task:
            await inner_message.answer(f"Задача с ID '{task_id}' отмечена как выполненная")
        else:
            await inner_message.answer(f"Не удалось задачу с ID {task_id}. Проверьте ID")