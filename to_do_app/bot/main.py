import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config_reader import config 
from handlers import setup_routers 

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",  # Настройка логирования
    )

    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML) # Инициализируем бота
    dp = Dispatcher() # Инициализируем диспетчера

    setup_routers(dp) # Подключаем роутеры

    await dp.start_polling(bot) # Запускаем polling

if __name__ == "__main__":
    asyncio.run(main())