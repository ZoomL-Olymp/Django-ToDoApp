from pydantic import SecretStr, BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    bot_token: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

config = Settings()