from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from Backend.db.session import get_bd

from DataBase.model import User
from schems import User_
from DataBase.requests import search_user, search_admin

app_reg = APIRouter(prefix="/reg", tags=["Reg"])


@app_reg.get('/user/{tg_id}', response_class=JSONResponse, status_code=200)
async def reg_user(tg_id: int, session = Depends(get_bd)):

    user = await search_user(session,tg_id=tg_id)
    user_json = jsonable_encoder({'user':user})
    return user_json

@app_reg.get('/admin/{tg_id}', response_class=JSONResponse, status_code=200)
async def reg_admin(tg_id: int, session = Depends(get_bd)):

    admin = await search_admin(session,tg_id=tg_id)
    admin_json = jsonable_encoder({'admin':admin})
    return admin_json

@app_reg.post('/add', response_class=JSONResponse, status_code=201)
async def reg_add(user: User_, session = Depends(get_bd)):
    user_or_admin = User(tg_id=user.tg_id, user_name=user.name, role= user.role)

    session.add(user_or_admin)
    await session.commit()
    await session.refresh(user_or_admin)
    user_json = jsonable_encoder({'tg_id': user_or_admin.tg_id, 'name': user_or_admin.user_name, 'role': user_or_admin.role})
    print(user_json)
    return  user_json

