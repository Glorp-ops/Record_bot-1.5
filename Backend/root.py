import datetime
from typing import Any

from fastapi import FastAPI, Depends, Body
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from watchfiles import awatch

from DataBase.database import async_session_maker
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from DataBase.model import User, Record, Lesson
from DataBase.requests import add_user_or_admin, search_user, search_admin, add_users_or_admins, info_records_users, \
    del_records, table_records, lessons_print, search_users_id, search_lessons, table_users


class Lesson_(BaseModel):
    name: str

class User_(BaseModel):
    tg_id: int
    name: str
    role: str

class Record_(BaseModel):
    date: datetime.date
    time: datetime.time
    tg_id: int
    lesson: str

app = FastAPI()

async def get_bd():
    async with async_session_maker() as session:
        yield session



@app.get('/reg/user/{tg_id}', response_class=JSONResponse, status_code=200)
async def reg_user(tg_id: int, session = Depends(get_bd)):

    user = await search_user(session,tg_id=tg_id)
    user_json = jsonable_encoder({'user':user})
    return user_json

@app.get('/reg/admin/{tg_id}', response_class=JSONResponse, status_code=200)
async def reg_admin(tg_id: int, session = Depends(get_bd)):

    admin = await search_admin(session,tg_id=tg_id)
    admin_json = jsonable_encoder({'admin':admin})
    return admin_json

@app.post('/reg/add', response_class=JSONResponse, status_code=201)
async def reg_add(user: User_, session = Depends(get_bd)):
    user_or_admin = User(tg_id=user.tg_id, user_name=user.name, role= user.role)

    session.add(user_or_admin)
    await session.commit()
    await session.refresh(user_or_admin)
    user_json = jsonable_encoder({'tg_id': user_or_admin.tg_id, 'name': user_or_admin.user_name, 'role': user_or_admin.role})
    print(user_json)
    return  user_json


@app.get('/del_record/user/{tg_id}', response_class=JSONResponse, status_code=200)
async def del_lesson_user(tg_id: int, session = Depends(get_bd)):

    info_record_user = await info_records_users(session, tg_id=tg_id)
    print(info_record_user)
    info_record_user_json = jsonable_encoder({'info_record_user':info_record_user})

    return info_record_user_json

@app.delete('/del_record/number/{tg_id}/{del_record}', response_class=JSONResponse, status_code=204)
async def del_lesson_number(tg_id: int, del_record: int , session = Depends(get_bd)):

    await del_records(session,tg_id=tg_id, del_record=del_record)

    return

@app.get('/booking/table/lessons', response_class=JSONResponse, status_code=200)
async def booking_table_lesson(session = Depends(get_bd)):

    lessons = await lessons_print(session)

    lessons_json = jsonable_encoder({'lessons_table':lessons})
    return lessons_json

@app.get('/booking/table/records/{tg_id}', response_class=JSONResponse, status_code=200)
async def booking_table_records(tg_id: int, session = Depends(get_bd)):

    data = await table_records(session, tg_id=tg_id)
    data_json = jsonable_encoder({'records_table': data})

    return data_json

@app.post('/booking', response_class=JSONResponse, status_code=201)
async def booking_records(reccord: Record_, session: AsyncSession = Depends(get_bd)):

    search_user_id = await session.execute(select(User).where(User.tg_id == reccord.tg_id))
    user_id = search_user_id.scalar_one()

    search_lesson_id = await session.execute(select(Lesson).where(Lesson.name == reccord.lesson))
    lesson_id = search_lesson_id.scalar_one()
    add_record = Record(user_id = user_id.id, lesson_id = lesson_id.id, date = reccord.date, time = reccord.time)
    session.add(add_record)

    await session.commit()
    await session.refresh(add_record)
    result_json = jsonable_encoder({'date': add_record.date, 'time': add_record.time, 'tg_id': add_record.user_id, 'lesson': add_record.lesson_id})

    return result_json
@app.get('/admin/search_lesson/{lesson_del}', response_class=JSONResponse, status_code=200)
async def admin_search_lesson(lesson_del: str ,session = Depends(get_bd)):

    lesson_del_db = await search_lessons(session, lesson_del=lesson_del)
    lesson_del_db_json = jsonable_encoder({'lesson_del':lesson_del_db})

    return lesson_del_db_json

@app.get('/admin/user_id', response_class=JSONResponse, status_code=200)
async def admin_user_id(session = Depends(get_bd)):

    user = await search_users_id(session)
    user_json = jsonable_encoder({'user_id': user})

    return user_json
@app.post('/admin/add_lesson',response_class=JSONResponse, status_code=201)
async def admin_add_lesson(lesson: Lesson_, session = Depends(get_bd)):

    add_lesson = Lesson(name=lesson.name)

    session.add(add_lesson)

    await session.commit()
    await session.refresh(add_lesson)

    result = jsonable_encoder({'add_lesson': add_lesson.name})

    return result
@app.delete('admin/delete_lesson/{lesson_del}', response_class=JSONResponse, status_code=204)
async def admin_delete_lesson(lesson_del: str, session = Depends(get_bd)):

    lesson_del_db = await search_lessons(session, lesson_del = lesson_del)
    await session.delete(lesson_del_db)
    await session.commit()

    return

@app.get('/admin/table/users', response_class=JSONResponse, status_code=200)
async def admin_table_users(session = Depends(get_bd)):

    data = await table_users(session)
    data_json = jsonable_encoder({'table_users':data})

    return data_json

@app.patch('/admin/upd_lessons', response_class=JSONResponse, status_code=200)
async def admin_upd_lessons(old_lesson: str = Body(embed=True), new_lesson: str = Body(embed=True),session = Depends(get_bd) ):

    await session.execute(
        update(Lesson)
        .where(Lesson.name == old_lesson)
        .values(name = new_lesson))

    await session.commit()

    result_json = jsonable_encoder({'old_lesson':old_lesson, 'new_lesson':new_lesson})
    return result_json

@app.get('/{tg_id}', response_class=JSONResponse, status_code=200)
async def start(tg_id: int, session = Depends(get_bd)):

    user = await add_user_or_admin(session ,tg_id=tg_id)
    user_dict = {'user_bd':user}
    user_json = jsonable_encoder(user_dict)

    return user_json

