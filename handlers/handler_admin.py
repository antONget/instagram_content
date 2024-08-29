from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter
from aiogram.exceptions import TelegramBadRequest

import keyboards.keyboard_admin as kb
import database.requests as rq
from filter.admin_filter import IsSuperAdmin
from config_data.config import Config, load_config
from secrets import token_urlsafe

import logging

config: Config = load_config()
router = Router()
user_dict = {}


class OrderPersonal(StatesGroup):
    set_amount = State()
    set_comment = State()
    search_id = State()
    link_resource = State()
    name_resource = State()


# Персонал
@router.message(F.text == 'Панель управления', IsSuperAdmin())
async def admin_mode_chapter(message: Message) -> None:
    """
    Нажата кнопка "Панель управления"
    :param message:
    :return:
    """
    logging.info(f'admin_mode_chapter: {message.chat.id}')
    await message.answer(text='Выберите действие!',
                         reply_markup=kb.keyboard_admin_mode())


@router.callback_query(F.data == 'get_content')
async def admin_mode_select_content(callback: CallbackQuery):
    """
    Выбор категории контента
    :param callback:
    :return:
    """
    logging.info(f'admin_mode_get_content: {callback.message.chat.id}')
    await callback.message.answer(text='Выберите категорию контента',
                                  reply_markup=await kb.keyboard_admin_content())
    await callback.answer()


@router.callback_query(F.data.startswith("type_content_"))
async def get_content_for_public(callback: CallbackQuery):
    """
    Получаем тип контента для предоставления на публикацию
    :param callback:
    :return:
    """
    logging.info(f'get_content_for_public')
    type_public = callback.data.split('_')[-1]
    list_order = await rq.get_orders_type_content(type_public=type_public)
    for order in list_order:
        order_id = order.id
        user_tg = order.tg_client
        resource = order.link_resource
        about_me = order.about_me
        user = await rq.get_user_tg_id(tg_id=int(user_tg))
        info = f'<b>О клиенте:</b>\n{about_me}\n' \
               f'<b>TG-uswername:</b>\n@{user.username}\n' \
               f'<b>Ресурс для размещения контента:</b>\n{resource}\n' \
               f'<b>Инстаграм клиента:</b>\n' \
               f'{user.link_personal}'
        if order.type_content == rq.OrderContent.text:
            await callback.message.answer(text=f'{order.content}\n\n{info}',
                                          reply_markup=kb.keyboard_published(order_id=order_id),
                                          parse_mode='html')
        elif order.type_content == rq.OrderContent.photo:

            await callback.message.answer_photo(photo=f'{order.content}',
                                                caption=f'{order.caption}\n\n{info}',
                                                reply_markup=kb.keyboard_published(order_id=order_id),
                                                parse_mode='html')
        elif order.type_content == rq.OrderContent.video:
            await callback.message.answer_video(video=f'{order.content}',
                                                caption=f'{order.caption}\n\n{info}',
                                                reply_markup=kb.keyboard_published(order_id=order_id),
                                                parse_mode='html')
    await callback.answer()


@router.callback_query(F.data.startswith("published_"))
async def set_order_complete(callback: CallbackQuery, bot: Bot):
    """
    Указываем что контент уже опубликован
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'set_order_complete')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    order_id = int(callback.data.split('_')[-1])
    await rq.set_order_executor(order_id=order_id, tg_executor=callback.message.chat.id)
    info_order = await rq.get_order_id(order_id=order_id)
    await rq.set_order_status(order_id=order_id)
    await bot.send_message(chat_id=info_order.tg_client,
                           text='Ваш материал опубликован у нас в профиле ✅.')
    await callback.answer(text='Контент помечен как "Опубликован"')


@router.callback_query(F.data.startswith("type_proposal_"))
async def get_proposal(callback: CallbackQuery):
    """
    Выгрузка предложений для просмотра
    :param callback:
    :return:
    """
    logging.info(f'get_proposal')
    type_proposal = callback.data.split('_')[-1]
    if type_proposal == 'barter':
        text = 'бартере'
    else:
        text = 'рекламе'
    list_proposal = await rq.get_proposal_type_status(type_proposal=type_proposal)
    for proposal in list_proposal:
        user = await rq.get_user_tg_id(tg_id=proposal.tg_id)
        await callback.message.answer(text=f'<b>Клиент</b>:\n@{user.username}/{user.tg_id}\n\n'
                                           f'<b>Предложение о {text}</b>:\n{proposal.proposal}',
                                      reply_markup=kb.keyboard_proposal_read(proposal_id=proposal.id),
                                      parse_mode='html')
    await callback.answer()


@router.callback_query(F.data.startswith("introduction_"))
async def set_introduction(callback: CallbackQuery, bot: Bot):
    """
    Помечаем что предложение просмотрено
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'set_introduction')
    proposal_id = int(callback.data.split('_')[-1])
    await rq.set_proposal_status(proposal_id=proposal_id)
    await callback.answer(text='Предложение переведено в статус "Ознакомлен"', show_alert=True)
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await callback.answer()


@router.callback_query(F.data == 'my_ref_link')
async def my_refer_link(callback: CallbackQuery) -> None:
    """
    Получаем меню реферальных ссылок [Сгененрировать, Статистика, Мои ссылки]
    :param callback:
    :return:
    """
    logging.info(f'my_refer_link: {callback.message.chat.id}')
    await callback.message.answer(text='Выберите раздел',
                                  reply_markup=kb.keyboard_refer())
    await callback.answer()


@router.callback_query(F.data.startswith("generate_token"))
async def process_generate_token(callback: CallbackQuery):
    """
    Генерация токена для выбранного ресурса
    :param callback:
    :return:
    """
    logging.info(f'process_generate_token')
    resources = [resource for resource in await rq.get_resources()]
    await callback.message.answer(text='Выберите ресурс для ссылки',
                                  reply_markup=kb.keyboards_select_resources(list_resources=resources))
    await callback.answer()


@router.callback_query(F.data.startswith("my_link"))
async def process_my_link(callback: CallbackQuery):
    """
    Вывод сформированных ссылок к ресурсам
    :param callback:
    :return:
    """
    logging.info(f'process_my_link')
    resources = await rq.get_resources()
    text = '<b>Ваши ссылки к ресурсам:</b>\n\n'
    for resource in resources:
        text += f'<i>Название ресурса:</i> {resource.name_resource}\n' \
                f'<i>Сcылка на ресурс:</i> {resource.link_resource}\n' \
                f'<i>Ссылка бота на ресурс:</i> ' \
                f'<code>https://t.me/meetuprus_bot?start={resource.token_resource}</code>\n\n'
    await callback.message.answer(text=text,
                                  parse_mode='html')
    await callback.answer()


@router.callback_query(F.data.startswith("resource_"))
async def process_select_resource(callback: CallbackQuery):
    """
    Сгенерированная реферальная ссылка для ресурса
    :param callback:
    :return:
    """
    logging.info(f'process_select_resource')
    resource_id = int(callback.data.split('_')[-1])
    info_resource = await rq.get_resource_id(resource_id=resource_id)
    token = str(token_urlsafe(8))
    await rq.set_resource_token(token=token, resource_id=resource_id)
    await callback.message.answer(text=f'Разместите ссылку:  <code>https://t.me/meetuprus_bot?start={token}</code>'
                                       f' на ресурсе: {info_resource.name_resource}',
                                  parse_mode='html')


@router.callback_query(F.data == "statistic")
async def process_get_statistic(callback: CallbackQuery):
    """
    Сатистистика переходов и оплаты контента
    :param callback:
    :return:
    """
    logging.info(f'process_get_statistic')
    orders = [order for order in await rq.get_orders()]
    users = [user for user in await rq.get_all_users()]
    resources = [resource for resource in await rq.get_resources()]
    # формируем словарь по списку пользователей
    statistic = {}
    for resource in resources:
        # ключ ссылка на ресурс
        resource = resource.link_resource
        if resource not in statistic.keys():
            statistic[resource] = []
    for user in users:
        # ключ ссылка на ресурс
        resource = user.link_resource
        if resource not in statistic.keys():
            statistic[resource] = [user.tg_id]
        else:
            statistic[resource].append(user.tg_id)

    text = '<b>Количество пользователей запустивших бота:</b>\n\n'
    for resource, list_client in statistic.items():
        info_resource = await rq.get_resource_link(link=resource)
        if info_resource:
            text += f'<i>Название ресурса:</i> {info_resource.name_resource}\n' \
                    f'<i>Сcылка на ресурс:</i> {info_resource.link_resource}\n' \
                    f'<i>Количество уникальных пользователей:</i> {len(list_client)}\n'
        else:
            continue
        text += f'<i>Количество пользователей оплативших единоразово контент:</i> ' \
                f'{len(set(await rq.get_orders_link(link=resource)))}\n'
        text += f'<i>Количество пользователей оплативших размещение контента несколько раз:</i>' \
                f' {len(await rq.get_orders_link(link=resource)) - len(set(await rq.get_orders_link(link=resource)))}\n\n'
    await callback.message.answer(text=text,
                                  parse_mode='html')


@router.callback_query(F.data == 'change_resource')
async def admin_mode_change_resource(callback: CallbackQuery):
    """
    Меню добавления и удаления ресурсов
    :param callback:
    :return:
    """
    logging.info(f'admin_mode_change_resource: {callback.message.chat.id}')
    await callback.message.answer(text='Здесь вы можете добавить ресурс или удалить его ',
                                  reply_markup=kb.keyboard_select_action_resource())
    await callback.answer()


@router.callback_query(F.data == 'action_resource_delete')
async def admin_mode_resource_delete(callback: CallbackQuery):
    """
    Выбор ресурса для его удаления
    :param callback:
    :return:
    """
    logging.info(f'admin_mode_resource_delete: {callback.message.chat.id}')
    list_resources = [resource for resource in await rq.get_resources()]
    await callback.message.answer(text='Выберите ресурс для удаления',
                                  reply_markup=kb.keyboards_delete_resources(list_resources=list_resources))
    await callback.answer()


@router.callback_query(F.data.startswith('delete_resource_'))
async def admin_mode_resource_delete(callback: CallbackQuery):
    """
    Удаление выбранного ресурса
    :param callback:
    :return:
    """
    logging.info(f'admin_mode_resource_delete: {callback.message.chat.id}')
    resource_id = int(callback.data.split('_')[-1])
    info_resource = await rq.get_resource_id(resource_id=resource_id)
    await rq.delete_resource(resource_id=resource_id)
    await callback.answer(text=f'Ресурс {info_resource.name_resource} успешно удален!', show_alert=True)


@router.callback_query(F.data == 'action_resource_add')
async def admin_mode_resource_add(callback: CallbackQuery, state: FSMContext):
    """
    Добавление ресурса
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'admin_mode_resource_add: {callback.message.chat.id}')
    await callback.message.answer(text='пришлите ссылку на ресурс')
    await state.set_state(OrderPersonal.link_resource)


@router.message(StateFilter(OrderPersonal.link_resource), F.text)
async def admin_mode_get_link_resource(message: Message, state: FSMContext):
    """
    Добавление ссылки к ресурсу
    :param message:
    :param state:
    :return:
    """
    logging.info(f'admin_mode_get_link_resource: {message.chat.id}')
    link_resource = message.text
    await state.update_data(link_resource=link_resource)
    await message.answer(text='пришлите название на ресурс')
    await state.set_state(OrderPersonal.name_resource)


@router.message(StateFilter(OrderPersonal.name_resource), F.text)
async def admin_mode_add_resource(message: Message, state: FSMContext):
    """
    Добавление название к ресурсу и добавления в БД
    :param message:
    :param state:
    :return:
    """
    logging.info(f'admin_mode_add_resource: {message.chat.id}')
    name_resource = message.text
    data = await state.get_data()
    data_resource = {"link_resource": data['link_resource'],
                     "name_resource": name_resource}
    await rq.add_resource(data=data_resource)
    await message.answer(text=f'Ресурс {name_resource} успешно добавлен')
    await state.set_state(default_state)


