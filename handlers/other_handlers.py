import asyncio

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import FSInputFile
from database.requests import get_all_users
from services.get_exel import list_users_to_exel
from config_data.config import Config, load_config

import logging

router = Router()
config: Config = load_config()


@router.callback_query()
async def all_callback(callback: CallbackQuery) -> None:
    logging.info(f'all_callback: {callback.message.chat.id} / {callback.data}')
    await callback.message.answer(text='Я вас не понимаю!')
    await callback.answer()


@router.message()
async def all_message(message: Message) -> None:
    logging.info(f'all_message {message.chat.id} / {message.text}')
    if message.photo:
        logging.info(f'all_message message.photo')
        print(message.photo[-1].file_id)

    if message.video:
        logging.info(f'all_message message.photo')
        print(message.video.file_id)

    if message.sticker:
        logging.info(f'all_message message.sticker')

    # команды доступные администраторам
    list_super_admin = list(map(int, config.tg_bot.admin_ids.split(',')))
    if message.chat.id in list_super_admin:
        logging.info(f'all_message message.admin')
        if message.text == '/get_logfile':
            logging.info(f'all_message message.admin./get_logfile')
            file_path = "py_log.log"
            await message.answer_document(FSInputFile(file_path))

        if message.text == '/get_dbfile':
            logging.info(f'all_message message.admin./get_dbfile')
            file_path = "database/db.sqlite3"
            await message.answer_document(FSInputFile(file_path))

        if message.text == '/get_listusers':
            logging.info(f'all_message message.admin./get_listusers')
            list_user = await get_all_users()
            text = 'Список пользователей:\n'
            for i, user in enumerate(list_user):
                text += f'{i+1}. @{user.username}/{user.tg_id}\n\n'
                if i % 10 == 0 and i > 0:
                    await asyncio.sleep(0.2)
                    await message.answer(text=text)
                    text = ''
            await message.answer(text=text)

        if message.text == '/get_exelusers':
            logging.info(f'all_message message.admin./get_exelusers')
            await list_users_to_exel()
            file_path = "list_user.xlsx"
            await message.answer_document(FSInputFile(file_path))

        else:
            await message.answer('Я вас не понимаю!')
