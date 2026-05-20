from fastapi import Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from Backend.db.session import get_bd

from Backend.schems import Record_
from DataBase.model import User, Lesson, Record
from DataBase.requests import table_records, lessons_print

app_booking = APIRouter(prefix='/booking', tags=['Booking'])
@app_booking.get('/table/lessons', response_class=JSONResponse, status_code=200)
async def booking_table_lesson(session = Depends(get_bd)):

    lessons = await lessons_print(session)

    lessons_json = jsonable_encoder({'lessons_table':lessons})
    return lessons_json

@app_booking.get('/table/records/{tg_id}', response_class=JSONResponse, status_code=200)
async def booking_table_records(tg_id: int, session = Depends(get_bd)):

    data = await table_records(session, tg_id=tg_id)
    data_json = jsonable_encoder({'records_table': data})

    return data_json

@app_booking.post('/', response_class=JSONResponse, status_code=201)
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