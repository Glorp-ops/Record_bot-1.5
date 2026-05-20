import datetime
from datetime import date, time
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from DataBase.model import Lesson, User, Record
from DataBase.database import async_session_maker
from sqlalchemy import *


async def add_user_or_admin(session: AsyncSession, tg_id: int):

    sel_tg_id = await session.execute(select(User).where(User.tg_id == tg_id))
    get_tg_id = sel_tg_id.scalar_one_or_none()

    return get_tg_id

async def search_user(session: AsyncSession, tg_id: int):

    sel_user = await session.execute(select(User).where(User.tg_id == tg_id))
    user = sel_user.scalar_one_or_none()

    return user

async def search_admin(session: AsyncSession, tg_id: int):

    sel_admin = await session.execute(select(User).where(User.tg_id == tg_id))
    admin = sel_admin.scalar_one_or_none()

    return admin

async def add_users_or_admins(session: AsyncSession, tg_id: int, name: str, role: str) -> None:

    user_or_admin = User(tg_id=tg_id, user_name=name, role= role)
    session.add(user_or_admin)
    await session.commit()
    await session.refresh(user_or_admin)

async def info_records_users(session: AsyncSession, tg_id: int):

    sel_user_id = await session.execute(select(User).where(User.tg_id == tg_id))
    user_id = sel_user_id.scalar_one()

    sel_info_record_user = await session.execute(select(Record).where(Record.user_id == user_id.id).limit(1))
    info_record_user = sel_info_record_user.scalar_one_or_none()

    return info_record_user

async def del_records(session: AsyncSession, tg_id: int, del_record: int):

    search_user_id = await session.execute(select(User).where(User.tg_id == tg_id))
    user_id = search_user_id.scalar_one()

    sel_lessons_name = await session.execute(select(Record).options(joinedload(Record.lesson)).order_by(Record.id).where(Record.user_id == user_id.id))
    lessons_name = sel_lessons_name.scalars()

    sel_del_record = await session.execute(select(Record).options(joinedload(Record.lesson)).order_by(Record.id).where(Record.user_id == user_id.id and Record.lesson.name == lessons_name.lesson.name[del_record['number_lesson']-1]))
    del_record = sel_del_record.scalar_one()


    await session.delete(del_record)
    await session.commit()

async def lessons_print(session: AsyncSession):

    sel_lessons_print = await session.execute(select(Lesson.name).order_by(Lesson.id))
    lessons = sel_lessons_print.scalars().all()

    return lessons

async def add_records(session: AsyncSession, date: date, time: time, tg_id: int, lesson: str):

    search_user_id = await session.execute(select(User).where(User.tg_id == tg_id))
    user_id = search_user_id.scalar_one()

    search_lesson_id = await session.execute(select(Lesson).where(Lesson.name == lesson))
    lesson_id = search_lesson_id.scalar_one()
    add_record = Record(user_id = user_id.id, lesson_id = lesson_id.id, date = date, time = time)
    session.add(add_record)

    await session.commit()
    await session.refresh(add_record)

async def table_records(session: AsyncSession, tg_id: int):

        sel_user_id = await session.execute(select(User).where(User.tg_id == tg_id))
        user_id = sel_user_id.scalar_one()


        search_record_user = await session.execute(select(Record).order_by(Record.id).options(joinedload(Record.lesson)).where(Record.user_id == user_id.id))
        records_user = search_record_user.scalars()
        search_data = await session.execute(select(Record).where(Record.user_id == user_id.id))
        data = search_data.scalars()
        search_time = await session.execute(select(Record).where(Record.user_id == user_id.id))
        time = search_time.scalars()
        search_records_id = await session.execute(select(Record).where(Record.user_id == user_id.id))
        records_id_bd = search_records_id.scalars()

        number = [str(record_id.id) for record_id in records_id_bd]
        name = [str(record_name.lesson.name) for record_name in records_user]
        data = [str(data.date) for data in data]
        time = [str(time.time)[:-3] for time in time]

        data = list(zip(number, name, data, time))

        return data



async def table_users(session: AsyncSession):

    sel_users_name = await session.execute(select(User).order_by(User.id))
    users_name = sel_users_name.scalars()

    sel_users_id = await session.execute(select(User).order_by(User.id))
    users_tg_id = sel_users_id.scalars()

    sel_user_role = await session.execute(select(User).order_by(User.id))
    user_role = sel_user_role.scalars()

    sel_user_id = await session.execute(select(User).order_by(User.id))
    user_id = sel_user_id.scalars()

    sel_number_user = await session.execute(select(User).order_by(User.id))
    number_user = sel_number_user.scalars()

    users_id_print = [str(user.id) for user in user_id]
    users_name_print = [user.user_name for user in users_name]
    users_tg_id_print = [str(user.tg_id) for user in users_tg_id]
    users_role_print = [str(user.role) for user in user_role]

    number_users = len([str(user.tg_id) for user in number_user])

    data = list(zip(users_id_print, users_name_print, users_tg_id_print, users_role_print))

    return number_users,data

async def search_users_id(session: AsyncSession)  :

    sel_users_id = await session.execute(select(User))
    users_tg_id = sel_users_id.scalars().all()

    return users_tg_id

async def add_lessons(session: AsyncSession, lesson: str):

    add_lesson = Lesson(name = lesson)

    session.add(add_lesson)

    await session.commit()
    await session.refresh(add_lesson)


async def upd_lessons(session: AsyncSession, lesson: str, new_lesson: str):

    await session.execute(
        update(Lesson)
        .where(Lesson.name == lesson)
        .values(name = new_lesson))

    await session.commit()

async def search_lessons(session: AsyncSession, lesson_del: str):
    sel_lesson_del = await session.execute(select(Lesson).where(Lesson.name == lesson_del))

    lesson_del_db = sel_lesson_del.scalar_one_or_none()

    return lesson_del_db

async def del_lessons(session: AsyncSession, lesson_del: str):

    lesson_del_db = await search_lessons(session, lesson_del = lesson_del)
    await session.delete(lesson_del_db)
    await session.commit()
