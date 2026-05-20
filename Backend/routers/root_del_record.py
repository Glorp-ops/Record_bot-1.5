from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from DataBase.requests import info_records_users, del_records
from Backend.db.session import get_bd

app_del_record = APIRouter(prefix='/del_record', tags=['Del_record'])

@app_del_record.get('/user/{tg_id}', response_class=JSONResponse, status_code=200)
async def del_lesson_user(tg_id: int, session = Depends(get_bd)):

    info_record_user = await info_records_users(session, tg_id=tg_id)
    print(info_record_user)
    info_record_user_json = jsonable_encoder({'info_record_user':info_record_user})

    return info_record_user_json

@app_del_record.delete('/number/{tg_id}/{del_record}', response_class=JSONResponse, status_code=204)
async def del_lesson_number(tg_id: int, del_record: int , session = Depends(get_bd)):

    await del_records(session,tg_id=tg_id, del_record=del_record)

    return