from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from bot.keyboards import main_keyboard, categories_keyboard
from bot.api_client import create_task, get_categories, get_tasks, delete_task_request, complete_task
from bot.utils import UserData  # WIP | placeholder
from aiogram.fsm.context import FSMContext
from bot.dialogs.task_dialog import TaskDialog, add_task_handler
from datetime import datetime

router = Router()

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
     #  ПРОВЕРКА НА None!
    if not category_id.isdigit():
        await callback_query.answer("Ошибка: Неверный ID категории.", show_alert=True)
        return  #  Выходим из обработчика

    await state.update_data(category=int(category_id))  #  Сохраняем как int
    data = await state.get_data()
    access_token, _ = await UserData.get_tokens(callback_query.from_user.id)
    created_task = await create_task(access_token, data) # Создаем задачу в БД

    if created_task:
        await callback_query.message.answer(f"Задача '{created_task['title']}' успешно создана!")
    else:
        await callback_query.message.answer("Не получилось создать задачу")
    await state.clear()  # Очищаем состояние
    await callback_query.answer()