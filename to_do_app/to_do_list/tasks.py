# to_do_list/tasks.py
from celery import shared_task
from django.contrib.auth.models import User
from .models import Task
from aiogram import Bot  # Import Bot from aiogram
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError  # Import for error handling
import os
import asyncio

# Get the bot token from the environment variable
bot_token = os.environ.get('BOT_TOKEN')
if not bot_token:
    raise ValueError("BOT_TOKEN environment variable not set!")

@shared_task
def send_notification(task_id):
    async def _send_notification():  # Inner async function
        try:
            task = await Task.objects.aget(pk=task_id)  # Use .aget()
            user = task.user
            if user.profile.telegram_id:
                bot = Bot(token=bot_token, parse_mode=ParseMode.HTML) # HTML parse mode
                try:
                    message = (f"Напоминание о задаче!\n\n"
                               f"ID: {task.user_task_id}\n"
                               f"Название: {task.title}\n"
                               f"Описание: {task.description or 'Нет описания'}\n"
                               f"Срок: {task.due_date.strftime('%Y-%m-%d %H:%M')}\n"
                               f"Категория: {task.category.name if task.category else 'Без категории'}\n"
                               f"Статус: {'Выполнено' if task.completed else 'Не выполнено'}")
                    await bot.send_message(chat_id=user.profile.telegram_id, text=message)
                    print(f"Sent notification for task {task_id} to user {user.profile.telegram_id}")
                finally:
                    await bot.session.close() # CLOSE SESSION
            else:
                print(f"User {user.username} (ID {user.pk}) has no telegram_id.  Cannot send notification.")

        except Task.DoesNotExist:
            print(f"Task with id {task_id} not found.")

        except TelegramAPIError as e: # Catch aiogram errors
            print(f"Telegram API error: {e}")

        except Exception as e:
            print(f"Error sending notification for task {task_id}: {e}")

    asyncio.run(_send_notification()) # Run async func