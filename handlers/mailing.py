import asyncio

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup

from filter.admin_filter import IsSuperAdmin
from database.requests import get_user_tg_id, get_all_users
from config_data.config import Config, load_config
import requests
import logging

router = Router()
config: Config = load_config()


class Mailing(StatesGroup):
    content = State()


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    return response.json()


@router.message(F.text == '/mailing', IsSuperAdmin())
async def mailing_message(message: Message, state: FSMContext) -> None:
    logging.info(f'mailing_message {message.chat.id}')
    if '/mailing' in message.text:
        logging.info(f'all_message-/send_message')
        send = message.text.split()
        if send[2] == "all":
            await message.answer(text='Пришлите контент чтобы его отправить всем пользователям бота')
            await state.update_data(id_user="all")
            await state.set_state(Mailing.content)
        elif len(send) == 2:
            try:
                id_user = int(send[2])
                info_user = await get_user_tg_id(id_user)
                if info_user:
                    result = get_telegram_user(user_id=id_user, bot_token=config.tg_bot.token)
                    if 'result' in result:
                        await message.answer(text=f'Пришлите контент чтобы его отправить пользователю'
                                                  f' @{info_user.username}')
                        await state.update_data(id_user=id_user)
                        await state.set_state(Mailing.content)
                    else:
                        await message.answer(text=f'Бот не нашел пользователя @{info_user.username}.'
                                                  f' Возможно он его заблокировал')
                else:
                    await message.answer(text=f'Бот не нашел пользователя {id_user} в БД')
            except:
                pass
        else:
            await message.answer(text=f'Пришлите после команды /mailing '
                                      f'id телеграм пользователя (например, /mailing 843554518)'
                                      f' - для отправки пользователю по его id;'
                                      f'all (/mailing all) - для отправки всем пользователям в БД.')


@router.message(StateFilter(Mailing.content))
async def get_content(message: Message, state: FSMContext):
    """
    Получаем контент от администратора
    :param message:
    :param state:
    :return:
    """
    logging.info(f'get_content {message.chat.id}')
    if message.photo:
        content_text = message.caption
        content_photo = message.photo[-1].file_id
    else:
        content_text = message.text
        content_photo = 'none'
    await state.update_data(content_text=content_text)
    await state.update_data(content_photo=content_photo)
    data = await state.get_data()
    button_1 = InlineKeyboardButton(text=f'Отправить',
                                    callback_data='mail_yes')
    button_2 = InlineKeyboardButton(text=f'Отмена',
                                    callback_data='mail_yes')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    if data['id_user'] == 'all':
        await message.answer(text=f'Отправить контент всем пользователя в из БД',
                             reply_markup=keyboard)
    else:
        info_user = await get_user_tg_id(data['id_user'])
        await message.answer(text=f'Отправить контент пользователю @{info_user.username}',
                             reply_markup=keyboard)


@router.callback_query(F.data.startswith('mail'))
async def mailing_content(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """

    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f"mailing_content")
    answer = callback.data.split("_")[-1]
    data = await state.get_data()
    id_user = data['id_user']
    content_photo = data['content_photo']
    if answer == 'yes':

        if id_user == 'all':
            list_users = await get_all_users()
            await callback.message.edit_text(text=f'Рассылка на {len(list_users)} пользователей запущена',
                                             reply_markup=None)
            count = 0
            for user in list_users:
                await asyncio.sleep(0.1)
                try:
                    if content_photo == 'none':
                        await bot.send_message(chat_id=user.tg_id,
                                               text=data['content_text'])
                    else:
                        await bot.send_photo(chat_id=user.tg_id,
                                             photo=content_photo,
                                             caption=data['content_text'])
                    count += 1
                except:
                    pass

            await callback.message.edit_text(text=f'Рассылку получили {count}/{len(list_users)} пользователей')
        else:
            try:
                if content_photo == 'none':
                    await bot.send_message(chat_id=id_user,
                                           text=data['content_text'])
                else:
                    await bot.send_photo(chat_id=id_user,
                                         photo=content_photo,
                                         caption=data['content_text'])
            except:
                pass
        await state.set_state(state=None)
    else:
        await callback.message.edit_text(text='Рассылка отменена',
                                         reply_markup=None)
