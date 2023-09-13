from functools import lru_cache
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    database_echo: bool = False
    database_pool_size: int = 20

    enable_swagger: bool = True


@lru_cache  # https://fastapi.tiangolo.com/advanced/settings/#settings-in-a-dependency
def get_settings():
    try:
        return Settings()
    except ValidationError as ve:
        details = [f'{error["loc"]}: {error["msg"]}' for error in ve.errors()]
        msg = f"Invalid settings:\n" + "\n".join(details)
        raise ValueError(msg) from ve
