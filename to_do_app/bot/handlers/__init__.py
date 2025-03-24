from aiogram import Router, F
from .common import command_start, command_help, command_logout
from .tasks import list_tasks, add_task, task_dialog, delete_task, done_task
from . import  dialogs
def setup_routers(dp: Router):
    # Создаем отдельные роутеры для каждой группы обработчиков
    common_router = Router()
    task_router = Router()

    # Регистрируем обработчики
    common_router.message.register(command_start, F.text == "/start")
    common_router.message.register(command_help, F.text == "/help")
    common_router.message.register(command_logout, F.text == "/logout")

    task_router.message.register(list_tasks, F.text == "/list")
    task_router.message.register(add_task, F.text == "/add")
    task_router.message.register(delete_task, F.text == "/delete")
    task_router.message.register(done_task, F.text == "/done")

    # Включаем роутеры в главный диспетчер
    dp.include_router(common_router)
    dp.include_router(task_router)
    dp.include_router(dialogs.task_dialog.router)