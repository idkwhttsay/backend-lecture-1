import os
from pathlib import Path
from os import getenv

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    name: str = "Tasks FastAPI App"
    postgres_user: str = getenv("POSTGRES_USER")
    postgres_password: str = getenv("POSTGRES_PASSWORD")
    postgres_db: str = getenv("POSTGRES_DB")
    postgres_host: str = getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(getenv("POSTGRES_PORT", 5432))
    secret_key: str = getenv("SECRET_KEY")
    algorithm: str = getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

settings = Settings()
