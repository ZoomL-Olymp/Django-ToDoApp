from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    bot_token: SecretStr
    secret_key: SecretStr = Field(..., env='SECRET_KEY')
    debug: bool = Field(True, env='DEBUG')

config = Settings()