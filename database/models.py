from sqlalchemy import BigInteger, ForeignKey, String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from typing import List

engine = create_async_engine(url="sqlite+aiosqlite:///database/db.sqlite3", echo=False)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(Integer, default=0)
    username: Mapped[str] = mapped_column(String(20))
    link_resource: Mapped[str] = mapped_column(String(200))
    link_personal: Mapped[str] = mapped_column(String(200), default='None')


class Resource(Base):
    __tablename__ = 'resources'

    id: Mapped[int] = mapped_column(primary_key=True)
    token_resource: Mapped[str] = mapped_column(String(20), default="None")
    link_resource: Mapped[str] = mapped_column(String(200))
    name_resource: Mapped[str] = mapped_column(String(200))


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(10))
    data_create: Mapped[str] = mapped_column(String(40))
    data_public: Mapped[str] = mapped_column(String(40), default='None')
    tg_client: Mapped[int] = mapped_column(Integer)
    link_resource: Mapped[str] = mapped_column(String(200))
    tg_executor: Mapped[int] = mapped_column(Integer, default='0')
    about_me: Mapped[str] = mapped_column(String)
    type_public: Mapped[str] = mapped_column(String)
    type_content: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)
    caption: Mapped[str] = mapped_column(String)


class Proposal(Base):
    __tablename__ = 'proposals'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String)
    tg_id: Mapped[int] = mapped_column(Integer)
    type_proposal: Mapped[str] = mapped_column(String)
    proposal: Mapped[str] = mapped_column(String)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# import asyncio
#
# asyncio.run(async_main())
