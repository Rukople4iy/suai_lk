from dataclasses import dataclass
from dotenv import load_dotenv
from .base import getenv


@dataclass
class TelegramBotConfig:
    token: str


@dataclass
class DbConfig:
    user: str
    password: str
    database: str
    host: str


@dataclass
class Config:
    tg_bot_main: TelegramBotConfig
    db: DbConfig
    api_key: str


def load_config() -> Config:
    load_dotenv()
    return Config(
        tg_bot_main=TelegramBotConfig(token=getenv("BOT_TOKEN")),
        db=DbConfig(
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            database=getenv("DB_NAME"),
            host=getenv("DB_HOST")
        ),
    )
