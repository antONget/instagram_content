from database.models import User, Resource, Order, Proposal
from database.models import async_session
from sqlalchemy import select, update, delete
from dataclasses import dataclass
import logging


"""USER"""


async def add_user(data: dict, token: str) -> bool | str:
    """
    Добавляем нового пользователя если его еще нет в БД
    :param data:
    :param token:
    :return:
    """
    logging.info(f'add_user')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == data['tg_id']))
        # если пользователя нет в базе
        if not user:
            # получаем токен на ресурс по которому он перешел
            resource = await get_resource_token(token=token)
            if resource:
                # получаем ссылку на ресурс
                link_resource = resource.link_resource
                # если пользователь в БД с таким ресурсом не существует, то мы обновляем его ресурс
                user_bd = await session.scalar(select(User).where(User.tg_id == data['tg_id'],
                                                                  User.link_resource == link_resource))
                if not user_bd:
                    data["link_resource"] = link_resource
                    session.add(User(**data))
                    await session.commit()
                    return 'change_link_resource'
                # иначе если пользователь снова перешел по этой же ссылке
                elif user_bd:
                    return 'user_alredy_in_bd'
                else:
                    return False
            # если переход по прямой ссылке
            else:
                data["link_resource"] = '/start'
                session.add(User(**data))
                await session.commit()
                return False
        # если пользователь уже БД
        else:
            # получаем ресурс по токену
            resource = await get_resource_token(token)
            # если ресурс есть обновляем ссылку
            if resource:
                user.link_resource = resource.link_resource
            else:
                return False


async def add_user_admin(data: dict) -> bool:
    """
    Добавляем нового пользователя если его еще нет в БД
    :param data:
    :return:
    """
    logging.info(f'add_user_admin')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == data['tg_id']))
        if not user:
            session.add(User(**data))
            await session.commit()


async def get_user_tg_id(tg_id: int) -> User:
    """
    Получаем информацию по пользователю
    :param tg_id:
    :return:
    """
    logging.info(f'get_user_tg_id')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user


async def get_users_link(link: str) -> User:
    """
    Получаем список пользователей перешедших по ссылке
    :param link:
    :return:
    """
    logging.info(f'get_user_tg_id')
    async with async_session() as session:
        users = await session.scalars(select(User).where(User.link_resource == link))
        return users


async def get_all_users() -> list[User]:
    """
    Получаем список всех пользователей зарегистрированных в боте
    :return:
    """
    logging.info(f'get_all_users')
    async with async_session() as session:
        users = await session.scalars(select(User))
        return users


async def set_user_link(tg_id: int, link: str) -> None:
    """
    Обновляем ссылку ресурса для пользователя перешедшего по прямой ссылке
    :param tg_id:
    :param link:
    :return:
    """
    logging.info(f'set_user_link')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.link_resource = link
            await session.commit()


async def set_user_link_personal(tg_id: int, link_personal: str) -> None:
    """
    Обновляем ссылку персональную ссылку пользователя
    :param tg_id:
    :param link_personal:
    :return:
    """
    logging.info(f'set_user_link_personal')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            if link_personal:
                user.link_personal = link_personal
                await session.commit()
            else:
                user.link_personal = 'None'
                await session.commit()

"""RESOURCE"""


async def add_resource(data: dict) -> None:
    """
    Добавляем новый ресурс в БД
    :param data:
    :return:
    """
    logging.info(f'add_resource')
    async with async_session() as session:
        session.add(Resource(**data))
        await session.commit()


async def get_resource_token(token: str) -> Resource:
    """
    Получаем ресурс по его токену
    :param token:
    :return:
    """
    logging.info(f'get_resource_token')
    async with async_session() as session:
        return await session.scalar(select(Resource).where(Resource.token_resource == token))


async def get_resource_id(resource_id: int) -> Resource:
    """
    Получаем ресурс по его id
    :param resource_id:
    :return:
    """
    logging.info(f'get_resource_id')
    async with async_session() as session:
        return await session.scalar(select(Resource).where(Resource.id == resource_id))


async def get_resource_link(link: str) -> Resource:
    """
    Получаем ресурс по его id
    :param link:
    :return:
    """
    logging.info(f'get_resource_link')
    async with async_session() as session:
        return await session.scalar(select(Resource).where(Resource.link_resource == link))


async def get_resources() -> list[Resource]:
    """
    Получаем ресурсы
    :return:
    """
    logging.info(f'get_resources')
    async with async_session() as session:
        return await session.scalars(select(Resource))


async def set_resource_token(token: str, resource_id: int) -> Resource:
    """
    Получаем ресурсы
    :param token:
    :param resource_id:
    :return:
    """
    logging.info(f'set_resource_token')
    async with async_session() as session:
        resource = await session.scalar(select(Resource).where(Resource.id == resource_id))
        resource.token_resource = token
        await session.commit()


async def delete_resource(resource_id: int) -> Resource:
    """
    Получаем ресурсы
    :param resource_id:
    :return:
    """
    logging.info(f'delete_resource')
    async with async_session() as session:
        resource = await session.scalar(select(Resource).where(Resource.id == resource_id))
        await session.delete(resource)
        await session.commit()


"""ORDER"""


@dataclass
class OrderStatus:
    payment = "payment"
    public = "public"


@dataclass
class OrderType:
    reels = "reels"
    public = "public"
    stories = "stories"


@dataclass
class OrderContent:
    text = "text"
    photo = "photo"
    video = "video"


async def add_order(data: dict) -> None:
    """
    Добавляем новый заказ на публикацию в БД
    :param data:
    :return:
    """
    logging.info(f'add_order')
    async with async_session() as session:
        session.add(Order(**data))
        await session.commit()


async def get_orders_type_content(type_public: str) -> Order:
    """
    Получаем информацию по пользователю
    :param type_public:
    :return:
    """
    logging.info(f'get_orders_type_content')
    async with async_session() as session:
        orders = await session.scalars(select(Order).where(Order.type_public == type_public,
                                                           Order.status == OrderStatus.payment))
        return orders.all()


async def get_order_id(order_id: int) -> Order:
    """
    Получаем заказ по его id
    :param order_id:
    :return:
    """
    logging.info(f'get_orders_type_content')
    async with async_session() as session:
        orders = await session.scalar(select(Order).where(Order.id == order_id))
        return orders


async def get_orders_link(link: str) -> list[Order]:
    """
    Получаем заказы по ссылке
    :param link:
    :return:
    """
    logging.info(f'get_orders_type_content')
    async with async_session() as session:
        orders = await session.scalars(select(Order).where(Order.link_resource == link))
        return orders.all()


async def get_orders() -> Order:
    """
    Получаем информацию по пользователю
    :return:
    """
    logging.info(f'set_order_status')
    async with async_session() as session:
        return await session.scalars(select(Order))


async def set_order_status(order_id: int) -> None:
    """
    Получаем информацию по пользователю
    :param order_id:
    :return:
    """
    logging.info(f'set_order_status')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.status = OrderStatus.public
        await session.commit()


async def set_order_executor(order_id: int, tg_executor: int) -> None:
    """
    Получаем информацию по пользователю
    :param order_id:
    :param tg_executor:
    :return:
    """
    logging.info(f'set_order_status')
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.tg_executor = tg_executor
        await session.commit()


"""PROPOSAL"""


@dataclass
class ProposalType:
    advertisement = "advertisement"
    barter = "barter"


@dataclass
class ProposalStatus:
    new = "new"
    viewed = "viewed"


async def add_proposal(data: dict) -> None:
    """
    Добавляем новое предложение в БД
    :param data:
    :return:
    """
    logging.info(f'add_proposal')
    async with async_session() as session:
        session.add(Proposal(**data))
        await session.commit()


async def get_proposal_type_status(type_proposal: str) -> list[Proposal]:
    """
    Получаем информацию по пользователю
    :param type_proposal:
    :return:
    """
    logging.info(f'get_orders_type_content')
    async with async_session() as session:
        proposal = await session.scalars(select(Proposal).where(Proposal.type_proposal == type_proposal,
                                                                Proposal.status == ProposalStatus.new))
        return proposal.all()


async def set_proposal_status(proposal_id: int) -> None:
    """
    Получаем информацию по пользователю
    :param proposal_id:
    :return:
    """
    logging.info(f'set_proposal_status')
    async with async_session() as session:
        proposal = await session.scalar(select(Proposal).where(Proposal.id == proposal_id))
        proposal.status = ProposalStatus.viewed
        await session.commit()
