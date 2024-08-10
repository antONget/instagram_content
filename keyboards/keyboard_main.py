from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import logging


def keyboards_main_admin() -> ReplyKeyboardMarkup:
    """
    Главная административное меню
    :return:
    """
    logging.info("keyboards_main")
    button_1 = KeyboardButton(text='Публикация')
    button_2 = KeyboardButton(text='Reels')
    button_3 = KeyboardButton(text='История')
    button_4 = KeyboardButton(text='Бартер')
    button_5 = KeyboardButton(text='Реклама')
    button_6 = KeyboardButton(text='Тех. поддержка')
    button_7 = KeyboardButton(text='Панель управления')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2], [button_3], [button_4, button_5], [button_6], [button_7]],
        resize_keyboard=True
    )
    return keyboard


def keyboards_main_user() -> ReplyKeyboardMarkup:
    """
    Главная административное меню
    :return:
    """
    logging.info("keyboards_main")
    button_1 = KeyboardButton(text='Публикация')
    button_2 = KeyboardButton(text='Reels')
    button_3 = KeyboardButton(text='История')
    button_4 = KeyboardButton(text='Бартер')
    button_5 = KeyboardButton(text='Реклама')
    button_6 = KeyboardButton(text='Тех. поддержка')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2], [button_3], [button_4, button_5], [button_6]],
        resize_keyboard=True
    )
    return keyboard


def keyboard_payment(payment_url: str, payment_id: int) -> None:
    logging.info("keyboard_select_period_sales")
    button_1 = InlineKeyboardButton(text='Проверить', callback_data=f'payment_{payment_id}')
    button_2 = InlineKeyboardButton(text='Оплатить', url=f'{payment_url}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard