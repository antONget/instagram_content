from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
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
    button_6 = KeyboardButton(text='Тех. поддержка 🧑‍💻')
    button_7 = KeyboardButton(text='Панель управления')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2], [button_3], [button_6], [button_7]],
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


def keyboard_payment(payment_url: str, payment_id: int, amount: str) -> None:
    logging.info("keyboard_select_period_sales")
    button_1 = InlineKeyboardButton(text='Проверить оплату', callback_data=f'payment_{payment_id}')
    button_2 = InlineKeyboardButton(text=f'Оплатить {amount} руб.', url=f'{payment_url}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard


def keyboards_attach_resources(list_resources: list) -> InlineKeyboardMarkup:
    logging.info(f"keyboards_attach_resources")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for resource in list_resources:
        text = resource.name_resource
        button = f'attach_resource_{resource.id}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()


def keyboard_confirm_select_resource() -> None:
    logging.info("keyboard_confirm_select_resource")
    button_1 = InlineKeyboardButton(text='Подтвердить', callback_data=f'confirm_select_resource')
    button_2 = InlineKeyboardButton(text='Назад', callback_data=f'back_select_resource')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard