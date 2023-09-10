from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import ValidationError


class Settings(BaseSettings):
    database_url: str
    database_echo: bool = False
    database_pool_size: int = 20

    enable_swagger: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache  # https://fastapi.tiangolo.com/advanced/settings/#settings-in-a-dependency
def get_settings():
    try:
        return Settings()
    except ValidationError as ve:
        details = [f'{error["loc"]}: {error["msg"]}' for error in ve.errors()]
        msg = f"Invalid settings:\n" + "\n".join(details)
        raise ValueError(msg) from ve
