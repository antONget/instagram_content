from config_data.config import load_config, Config
from aiogram.filters import BaseFilter
from aiogram.types import Message
import database.requests as rq
import logging

config: Config = load_config()


async def check_super_admin(telegram_id: int) -> bool:
    """
    Проверка на администратора
    :param telegram_id: id пользователя телеграм
    :return: true если пользователь администратор, false в противном случае
    """
    logging.info('cheсk_manager')
    list_super_admin = config.tg_bot.admin_ids.split(',')
    return str(telegram_id) in list_super_admin


class IsSuperAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return await check_super_admin(telegram_id=message.chat.id)

