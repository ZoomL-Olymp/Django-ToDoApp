from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings
from typing import Optional
import os  # Добавь импорт os
from dotenv import load_dotenv # Импортируем функцию
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)  # Явно загружаем .env

class Settings(BaseSettings):
    bot_token: SecretStr

    class Config:
        env_file = env_path
        env_file_encoding = 'utf-8'

config = Settings()