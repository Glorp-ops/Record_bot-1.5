from fastapi import Depends, Body, APIRouter
from fastapi.encoders import jsonable_encoder
from sqlalchemy import update
from starlette.responses import JSONResponse
from Backend.db.session import get_bd

from Backend.schems import Lesson_
from DataBase.model import Lesson
from DataBase.requests import search_lessons, search_users_id, table_users

app_admin = APIRouter(prefix='/admin', tags=['Admin'])

@app_admin.get('/search_lesson/{lesson_del}', response_class=JSONResponse, status_code=200)
async def admin_search_lesson(lesson_del: str ,session = Depends(get_bd)):

    lesson_del_db = await search_lessons(session, lesson_del=lesson_del)
    lesson_del_db_json = jsonable_encoder({'lesson_del':lesson_del_db})

    return lesson_del_db_json

@app_admin.get('/user_id', response_class=JSONResponse, status_code=200)
async def admin_user_id(session = Depends(get_bd)):

    user = await search_users_id(session)
    user_json = jsonable_encoder({'user_id': user})

    return user_json
@app_admin.post('/add_lesson',response_class=JSONResponse, status_code=201)
async def admin_add_lesson(lesson: Lesson_, session = Depends(get_bd)):

    add_lesson = Lesson(name=lesson.name)

    session.add(add_lesson)

    await session.commit()
    await session.refresh(add_lesson)

    result = jsonable_encoder({'add_lesson': add_lesson.name})

    return result
@app_admin.delete('/delete_lesson/{lesson_del}', response_class=JSONResponse, status_code=204)
async def admin_delete_lesson(lesson_del: str, session = Depends(get_bd)):

    lesson_del_db = await search_lessons(session, lesson_del = lesson_del)
    await session.delete(lesson_del_db)
    await session.commit()

    return

@app_admin.get('/table/users', response_class=JSONResponse, status_code=200)
async def admin_table_users(session = Depends(get_bd)):

    data = await table_users(session)
    data_json = jsonable_encoder({'table_users':data})

    return data_json

@app_admin.patch('/upd_lessons', response_class=JSONResponse, status_code=200)
async def admin_upd_lessons(old_lesson: str = Body(embed=True), new_lesson: str = Body(embed=True),session = Depends(get_bd) ):

    await session.execute(
        update(Lesson)
        .where(Lesson.name == old_lesson)
        .values(name = new_lesson))

    await session.commit()

    result_json = jsonable_encoder({'old_lesson':old_lesson, 'new_lesson':new_lesson})
    return result_json
