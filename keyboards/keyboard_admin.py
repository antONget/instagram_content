from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import database.requests as rq
import logging


def keyboard_admin_mode() -> InlineKeyboardMarkup:
    """
    Клавиатура разделов админ режима
    :return:
    """
    button_1 = InlineKeyboardButton(text=f'Получить контент',
                                    callback_data='get_content')
    button_2 = InlineKeyboardButton(text=f'Мои реферальные ссылки',
                                    callback_data='my_ref_link')
    button_3 = InlineKeyboardButton(text=f'Ресурсы',
                                    callback_data='change_resource')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]])
    return keyboard


async def keyboard_admin_content() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора заказов с определенным статусом
    :return:
    """
    button_1 = InlineKeyboardButton(text=f'Публикация ({len(await rq.get_orders_type_content(rq.OrderType.public))})',
                                    callback_data='type_content_public')
    button_2 = InlineKeyboardButton(text=f'Reels ({len(await rq.get_orders_type_content(rq.OrderType.reels))})',
                                    callback_data='type_content_reels')
    button_3 = InlineKeyboardButton(text=f'История ({len(await rq.get_orders_type_content(rq.OrderType.stories))})',
                                    callback_data='type_content_stories')
    button_4 = InlineKeyboardButton(
        text=f'Реклама ({len(await rq.get_proposal_type_status(rq.ProposalType.advertisement))})',
        callback_data='type_proposal_advertisement')
    button_5 = InlineKeyboardButton(
        text=f'Бартер ({len(await rq.get_proposal_type_status(rq.ProposalType.barter))})',
        callback_data='type_proposal_barter')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4, button_5],])
    return keyboard


def keyboard_published(order_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура разделов админ режима
    :return:
    """
    button_1 = InlineKeyboardButton(text=f'Опубликован',
                                    callback_data=f'published_{order_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1],])
    return keyboard


def keyboard_refer() -> InlineKeyboardMarkup:
    """
    Клавиатура разделов админ режима
    :return:
    """
    button_1 = InlineKeyboardButton(text=f'Сгенерировать',
                                    callback_data=f'generate_token')
    button_2 = InlineKeyboardButton(text=f'Статистика по ссылкам',
                                    callback_data=f'statistic')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboards_select_resources(list_resources: list):
    logging.info(f"keyboards_select_resources")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for resource in list_resources:
        text = resource.name_resource
        button = f'resource_{resource.id}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()


def keyboard_select_action_resource() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text=f'Добавить',
                                    callback_data=f'action_resource_add')
    button_2 = InlineKeyboardButton(text=f'Удалить',
                                    callback_data=f'action_resource_delete')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboards_delete_resources(list_resources: list):
    logging.info(f"keyboards_delete_resources")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for resource in list_resources:
        text = resource.name_resource
        button = f'delete_resource_{resource.id}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()


def keyboard_proposal_read(proposal_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура предложение/бартер - прочитано
    :return:
    """
    button_1 = InlineKeyboardButton(text=f'Ознакомлен',
                                    callback_data=f'introduction_{proposal_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1],])
    return keyboard
