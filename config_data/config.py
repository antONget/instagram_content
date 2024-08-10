from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: str
    support_id: int
    support_username: str
    yookassa_key: str
    yookassa_id: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               admin_ids=env('ADMIN_IDS'),
                               support_id=env('SUPPORT_ID'),
                               support_username=env('SUPPORT_USERNAME'),
                               yookassa_key=env('YOOKASSA_KEY'),
                               yookassa_id=env('YOOKASSA_ID')))
