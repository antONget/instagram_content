from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter, CommandObject, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state


from config_data.config import Config, load_config
import database.requests as rq
import keyboards.keyboard_main as kb
from filter.admin_filter import check_super_admin
from services.payments import create_payment, check_payment

from datetime import datetime
import logging

router = Router()
config: Config = load_config()


class Stage(StatesGroup):
    proposal = State()
    about_me = State()
    content = State()
    personal = State()


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext, command: CommandObject, bot: Bot) -> None:
    """
    Запуск бота - нажата кнопка "Начать" или введена команда "/start"
    :param message:
    :param state:
    :param command:
    :param bot:
    :return:
    """
    logging.info(f"process_start_command {message.chat.id}")
    await state.set_state(default_state)
    args = command.args
    # переход по ссылке
    if args:
        # если у пользователя есть username
        if message.from_user.username:
            username = message.from_user.username
        else:
            username = 'None'
        # добавляем пользователя в БД
        data = {"tg_id": message.chat.id,
                "username": username}
        user_bd = await rq.add_user(data=data, token=args)
        if not user_bd:
            await bot.send_message(chat_id=config.tg_bot.support_id,
                                   text=f'Пользователь не добавлен в БД {data}')
        elif user_bd == 'change_link_resource':
            await bot.send_message(chat_id=config.tg_bot.support_id,
                                   text=f'У пользователя обновлена ссылка {data} - {args}')
            if await check_super_admin(telegram_id=message.chat.id):
                await message.answer(text=f'Приветственное сообщение',
                                     reply_markup=kb.keyboards_main_admin())
            else:
                await message.answer(text=f'Приветственное сообщение',
                                     reply_markup=kb.keyboards_main_user())
        elif user_bd == 'user_alredy_in_bd':
            await bot.send_message(chat_id=config.tg_bot.support_id,
                                   text=f'Пользователь уже в БД с такой ссылкой {data} - {args}')
            if await check_super_admin(telegram_id=message.chat.id):
                await message.answer(text=f'Приветственное сообщение',
                                     reply_markup=kb.keyboards_main_admin())
            else:
                await message.answer(text=f'Приветственное сообщение',
                                     reply_markup=kb.keyboards_main_user())
    # переход без ссылки
    else:
        # админ
        if await check_super_admin(telegram_id=message.chat.id):
            await message.answer(text=f'Приветственное сообщение',
                                 reply_markup=kb.keyboards_main_admin())
            if message.from_user.username:
                username = message.from_user.username
            else:
                username = 'None'
            data = {"tg_id": message.chat.id,
                    "username": username,
                    "link_resource": "admin",
                    "link_personal": "admin"}
            await rq.add_user_admin(data=data)
        # не админ
        else:
            await bot.send_message(chat_id=config.tg_bot.support_id,
                                   text=f'Пользователь @{message.from_user.username}/{message.chat.id}'
                                        f' перешел по прямой ссылке')
            if message.from_user.username:
                username = message.from_user.username
            else:
                username = 'None'
            data = {"tg_id": message.chat.id,
                    "username": username}
            await rq.add_user(data=data, token='None')
            resources = await rq.get_resources()
            await message.answer(text='Вы перешли по прямой ссылке. Выберите ресурс для размещения на нем вашего'
                                      ' контента',
                                 reply_markup=kb.keyboards_attach_resources(list_resources=resources))


@router.callback_query(F.data.startswith('attach_resource_'))
async def attach_resource_user(callback: CallbackQuery, state: FSMContext):
    """
    Выбор пользователем перешедшим в бот по прямой ссылке ресурса
    :param callback:
    :param state:
    :return:
    """
    logging.info(f"attach_resource_user {callback.message.chat.id}")
    resource_id = int(callback.data.split('_')[-1])
    await state.update_data(resource_id=resource_id)
    info_resource = await rq.get_resource_id(resource_id=resource_id)
    await callback.message.edit_text(text=f'Вы выбрали.'
                                          f'<i>Название ресурса:</i> {info_resource.name_resource}\n'
                                          f'<i>Ссылка на ресурс:</i> {info_resource.link_resource}\n\n'
                                          f'Подтвердить?',
                                     reply_markup=kb.keyboard_confirm_select_resource(),
                                     parse_mode='html')
    await callback.answer()


@router.callback_query(F.data == 'confirm_select_resource')
async def confirm_select_resource(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Подтверждение выбранного ресурса для прикрепления его к профилю пользователя
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'confirm_select_resource {callback.message.chat.id}')
    data = await state.get_data()
    resource_id = data['resource_id']
    resource_info = await rq.get_resource_id(resource_id=resource_id)
    await rq.set_user_link(tg_id=callback.message.chat.id,
                           link=resource_info.link_resource)
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await callback.message.answer(text=f'Ресурс {resource_info.name_resource} успешно прикреплен к вашему профилю.\n'
                                       f'Выберите раздел',
                                  reply_markup=kb.keyboards_main_user())
    await callback.answer()


@router.callback_query(F.data == 'back_select_resource')
async def back_select_resource(callback: CallbackQuery, state: FSMContext):
    """
    Омена добавления к профилю пользователя выбранного ресурса
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'back_select_resource {callback.message.chat.id}')
    resources = await rq.get_resources()
    await callback.message.edit_text(text='Выберите ресурс для прикрепления его к вашему профилю',
                                     reply_markup=kb.keyboards_attach_resources(list_resources=resources))
    await state.clear()
    await callback.answer()


@router.message(or_f(F.text == 'Бартер', F.text == 'Реклама'))
async def get_proposal(message: Message, state: FSMContext) -> None:
    """
    Запрашиваем предложение - реклама/бартер
    :param message:
    :param state:
    :return:
    """
    logging.info(f'get_proposal {message.chat.id}')
    await message.answer(text=f'Напишите ваше предложение для нас ⬇️')
    await state.update_data(proposal=message.text)
    await state.set_state(Stage.proposal)


@router.message(StateFilter(Stage.proposal), F.text)
async def send_proposal(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем предложение - реклама/бартер
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'send_proposal {message.chat.id}')
    await message.answer(text='Спасибо, ваше предложение отправлено администратору, мы скоро с вами свяжемся ❤️')
    data = await state.get_data()
    proposal = data['proposal']

    if proposal == 'Бартер':
        temp = 'бартере'
        type_proposal = rq.ProposalType.barter
    elif proposal == 'Реклама':
        temp = 'рекламе'
        type_proposal = rq.ProposalType.advertisement
    data_proposal = {"tg_id": message.chat.id,
                     "status": rq.ProposalStatus.new,
                     "type_proposal": type_proposal,
                     "proposal": message.html_text}
    await rq.add_proposal(data=data_proposal)
    for admin in config.tg_bot.admin_ids.split(','):
        try:
            await bot.send_message(chat_id=int(admin),
                                   text=f'От пользователя @{message.from_user.username} поступило предложение о'
                                        f' {temp} {message.text}')
        except IndexError:
            pass
    await state.set_state(default_state)


@router.message(F.text == "Тех. поддержка")
async def support(message: Message) -> None:
    """
    Сообщаем кому задать вопрос
    :param message:
    :return:
    """
    logging.info(f'support {message.chat.id}')
    await message.answer(text=f'Если возникли вопросы или сложности при работе с ботом, то можете обратиться'
                              f' к {config.tg_bot.support_username}')


@router.message(or_f(F.text == 'Публикация', F.text == 'Reels', F.text == 'История'))
async def request_self(message: Message, state: FSMContext) -> None:
    """
    Информация пользователя
    :param message:
    :param state:
    :return:
    """
    logging.info(f'request_self {message.chat.id}')
    if message.text == 'Публикация':
        await state.update_data(type_public=rq.OrderType.public)
    elif message.text == 'Reels':
        await state.update_data(type_public=rq.OrderType.reels)
    elif message.text == 'История':
        await state.update_data(type_public=rq.OrderType.stories)
    await message.answer(text=f'Расскажите о себе ⭐\n\n'
                              f'Вы можете написать свое имя, возраст, город или страну проживания. Указать интересную'
                              f' информацию, например: хобби, увлечения, профессия, знак зодиака и предпочтения.\n\n'
                              f'Поделитесь, кого вы хотите найти или чем заняться на нашем сайте, дайте волю своей'
                              f' фантазии💗\n\n'
                              f'Вы можете написать абсолютно любое описание, но помните, что оно будет в открытом'
                              f' доступе у нас на странице!🫢')
    await state.set_state(Stage.about_me)


@router.message(StateFilter(Stage.about_me), F.text)
async def request_content_about_me(message: Message, state: FSMContext):
    """
    Получаем сообщение пользователя с рассказом о себе
    :param message:
    :param state:
    :return:
    """
    logging.info(f'request_content_about_me {message.chat.id}')
    about_me = message.text
    await state.update_data(about_me=about_me)
    await message.answer(text=f'📎 Прикрепите своё фото (можно несколько) или видео (больше охватов, чем у фото),'
                              f' которое вы хотите разместить в своей анкете.')
    await state.set_state(Stage.content)


@router.message(StateFilter(Stage.content), or_f(F.text, F.photo, F.video))
async def request_content_photo_text(message: Message, state: FSMContext):
    """
    Получаем от пользователя контент для публикации
    :param message:
    :param state:
    :return:
    """
    logging.info(f'request_content_photo_text {message.chat.id}')
    if message.text:
        await request_content_about_me(message=message, state=state)
        return
    elif message.photo:
        content = message.photo[-1].file_id
        caption = message.caption
        await state.update_data(caption=caption)
        await state.update_data(type_content=rq.OrderContent.photo)
    elif message.video:
        content = message.video.file_id
        caption = message.caption
        await state.update_data(caption=caption)
        await state.update_data(type_content=rq.OrderContent.video)
    await state.update_data(content=content)
    await message.answer(text=f'👉Пришлите ссылку на свой инстаграм, для отметки вашего профиля в публикации.\n\n'
                              f'🫢Если хотите остаться анонимными, пришлите ответным сообщением «Анон»')
    await state.set_state(Stage.personal)


@router.message(StateFilter(Stage.personal))
async def request_pay(message: Message, state: FSMContext):
    """
    Запрос оплаты
    :param message:
    :param state:
    :return:
    """
    logging.info(f'request_pay {message.chat.id}')
    personal = message.text
    await state.update_data(personal=personal)
    await rq.set_user_link_personal(tg_id=message.chat.id, link_personal=personal)
    data = await state.get_data()
    type_public = data['type_public']
    if type_public == rq.OrderType.public:
        amount = "350"
    elif type_public == rq.OrderType.reels:
        amount = "500"
    elif type_public == rq.OrderType.stories:
        amount = "300"
    payment_url, payment_id = create_payment(amount=amount, chat_id=message.chat.id, content=type_public)
    await message.answer(text=f'Оплатите размещение контента, после оплаты нажмите на кнопку «Проверить оплату» ⬇️ и'
                              f' ваша заявка на размещение поступит администратору',
                         reply_markup=kb.keyboard_payment(payment_url=payment_url,
                                                          payment_id=payment_id,
                                                          amount=amount))
    await state.set_state(default_state)


@router.callback_query(F.data.startswith('payment_'))
async def check_pay(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Проверка оплаты
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'check_pay {callback.message.chat.id}')
    payment_id = callback.data.split('_')[1]
    result = check_payment(payment_id=payment_id)
    if result == 'succeeded':
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
        await callback.answer(text='Платеж прошел успешно', show_alert=True)
        data = await state.get_data()
        user_info = await rq.get_user_tg_id(tg_id=callback.message.chat.id)
        data_order = {"status": rq.OrderStatus.payment,
                      "data_create": datetime.today().strftime('%H/%M/%S/%d/%m/%Y'),
                      "tg_client": callback.message.chat.id,
                      "link_resource": user_info.link_resource,
                      "about_me": data["about_me"],
                      "type_public": data["type_public"],
                      "type_content": data["type_content"],
                      "content": data["content"],
                      "caption": data["caption"]}
        await rq.add_order(data=data_order)
        await callback.message.answer(text='Материалы для публикации переданы менеджеру')
        list_admins = config.tg_bot.admin_ids.split(',')
        for admin in list_admins:
            try:
                await bot.send_message(chat_id=int(admin),
                                       text=f'Пользователь @{callback.from_user.username} оплатил размещение'
                                            f' {data["type_public"]}')
            except:
                pass
    else:
        await callback.message.answer(text='Платеж не прошел')
    await callback.answer()

