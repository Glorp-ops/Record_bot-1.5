import asyncio
import datetime
import os
from sqlalchemy.exc import IntegrityError
import sqlalchemy
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from main import TOKEN
from State.edit_lessons import EditLessons
from DataBase.model import User, Lesson,Record
from sqlalchemy import *
from sqlalchemy.orm import joinedload
from Middleware.middleware import LoggerMiddlewareMessage,LoggerMiddlewareCallback
from State.reg import  Reg
from State.record_del import RecordDel
from State.record_lesson import RecordLesson
from Keyboards.KeyBoards import register_keyboard,keyboard_menu,lessons_keyboard,edit_lessons_keyboard
from aiogram import F,Router,Bot
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from State.send_message import SendMessage
from tabulate import tabulate
from dotenv import load_dotenv
from json import loads
load_dotenv()

rt = Router()
bot = Bot(token=TOKEN)

str_admins = os.getenv('ADMIN_ID')
admins = loads(str_admins)

rt.message.middleware(LoggerMiddlewareMessage())
rt.callback_query.middleware(LoggerMiddlewareCallback())





    # Command handler
@rt.message(CommandStart(),StateFilter(None))
async def command_start_handler(message: Message,session) -> None:
    search_tg_id = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    tg_id = search_tg_id.scalar_one_or_none()

    if tg_id == None and message.from_user.id not in admins:

        await message.answer("Я тг бот для записи на занятия \n\n"
                             "Основыне команды:\n"
                             "/start - перезапуск бота\n"
                             "/end - завершение кого ли процесса\n"
                             
                             "Чтобы записаться на занятия зарегестрируете аккаунт ", reply_markup=register_keyboard())
    if tg_id != None and message.from_user.id not in admins:


        await message.answer(f"Здравствуйте,{tg_id.user_name}! \n"
                             "Что вы сегодня хотите сделать?", reply_markup=keyboard_menu())

    if message.from_user.id in admins and tg_id != None:

        await message.answer("Здравствуйте, админ! Вот ваши команды:\n"
                             "/all - посмотреть всех пользователей\n"
                             "/send_message - отправить сообщения всем пользователям\n"
                             "/edit_lessons - редактировать уроки\n"
                             "Что вы сегодня хотите сделать?", reply_markup=keyboard_menu())





@rt.message(Command('end'))
async def cmd_end(message: Message, state: FSMContext):

    await state.clear()

    await message.answer('Процесс закончен', reply_markup=ReplyKeyboardRemove())




@rt.message(Command('all'), StateFilter(None) , F.from_user.id.in_(admins))
async def cmd_all(message: Message,session):

    search_user_id = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user_id = search_user_id.scalar_one()

    sel_info_record_user = await session.execute(select(Record).where(Record.user_id == user_id.id))
    info_record_user = sel_info_record_user.scalar_one_or_none()

    if info_record_user == None:
        await message.answer('У вас нет записей')

    else:

        sel_users_name =  await session.execute(select(User).order_by(User.id))
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

        data = list(zip(users_id_print,users_name_print,users_tg_id_print,users_role_print))


        await message.answer(f'Количество: {number_users}\n'
                             f'<pre> {tabulate(data, headers=['Id', 'Имя', 'tg_id', 'Роль'] ,tablefmt='psql', stralign='center', numalign='center' )} </pre> ', parse_mode='HTML')

@rt.message(Command('send_message'), F.from_user.id.in_(admins))
async def cmd_send_message_command(message: Message, state: FSMContext):
    await state.set_state(SendMessage.message)
    await message.answer('Введите какой текст, который вы хотите отправить всем: ')

@rt.message(SendMessage.message)
async def cmd_send_message(message: Message, state: FSMContext, session):

    await state.update_data(message = message.text)

    send_message = await state.get_data()

    sel_users_id = await session.execute(select(User))
    users_tg_id = sel_users_id.scalars()

    text = f'Сообщение от админа: "{send_message['message']}"  '

    for user_tg_id in users_tg_id:
        try:
            await bot.send_message(user_tg_id.tg_id, text)
            await asyncio.sleep(0,5)

        except:
            pass

@rt.message(Command('edit_lessons'), StateFilter(None) , F.from_user.id.in_(admins) )
async def cmd_edit_lessons(message: Message):

    await message.answer('Что вы хотите сделать? ', reply_markup=edit_lessons_keyboard())

@rt.callback_query(F.data == 'add_lesson')
async def cmd_add_lesson_callback(callback: CallbackQuery, state: FSMContext, session):
    await callback.answer()

    lessons_print = await session.execute(select(Lesson.name).order_by(Lesson.id))
    lessons = lessons_print.fetchall()

    result = f'\n'.join([lesson_item.name for lesson_item in lessons])

    await callback.message.answer('Вот наши уроки:\n\n'
        f'{result} ', reply_markup=lessons_keyboard(lessons))

    await callback.message.answer('Какой урок вы хотите добавить (введите команду /end, чтобы прекратить процесс) ?')
    await state.set_state(EditLessons.add_lesson)

@rt.message(EditLessons.add_lesson)
async def cmd_add_lesson(message: Message, state: FSMContext, session):

    await state.update_data(lesson = message.text)
    lesson = await state.get_data()

    add_lesson = Lesson(name = lesson['lesson'])

    session.add(add_lesson)

    await session.commit()


    sel_users_id = await session.execute(select(User))
    users_tg_id = sel_users_id.scalars()

    text = f'Урок "{lesson['lesson']}" добавили '

    for user_tg_id in users_tg_id:
        try:
            await bot.send_message(user_tg_id.tg_id, text)
            await asyncio.sleep(0, 5)

        except:
            pass

    lessons_print = await session.execute(select(Lesson.name).order_by(Lesson.id))
    lessons = lessons_print.fetchall()

    result = f'\n'.join([lesson_item.name for lesson_item in lessons])

    await message.answer('Вы хотите что еще добавить?\n\n'
        f'{result} ', reply_markup=lessons_keyboard(lessons))


@rt.callback_query(F.data == 'upd_lesson')
async def cmd_upd_lesson_callback(callback: CallbackQuery, state: FSMContext, session):

    await callback.answer()

    lessons_print = await session.execute(select(Lesson.name).order_by(Lesson.id))
    lessons = lessons_print.fetchall()

    result = f'\n'.join([lesson_item.name for lesson_item in lessons])

    await callback.message.answer('Вот наши уроки: \n\n'
                         f'{result} ', reply_markup=lessons_keyboard(lessons))

    await state.set_state(EditLessons.upd_lesson)

    await callback.message.answer('Какой урок вы хотите изменить (введите команду /end, чтобы прекратить процесс) ?')

@rt.message(EditLessons.upd_lesson)
async def cmd_upd_lesson(message: Message, state: FSMContext):
    global lesson

    await state.update_data(lesson = message.text)

    lesson = await state.get_data()

    await state.set_state(EditLessons.new_lesson)

    await message.answer(f'На какой урок вы хотите заменить "{lesson['lesson']} " ?', reply_markup=ReplyKeyboardRemove())


@rt.message(EditLessons.new_lesson)
async def cmd_new_lesson(message: Message, state: FSMContext, session):
    global lesson, new_lesson

    await state.update_data(lesson_upd = message.text)

    new_lesson = await state.get_data()
    print(new_lesson['lesson_upd'])

    await session.execute(
        update(Lesson)
        .where(Lesson.name == lesson['lesson'])
        .values(name = new_lesson['lesson_upd']))

    await session.commit()

    sel_users_id = await session.execute(select(User))
    users_tg_id = sel_users_id.scalars()

    text = f'Урок "{lesson['lesson']}" изменили на "{new_lesson['lesson_upd']}"  '

    for user_tg_id in users_tg_id:
        try:
            await bot.send_message(user_tg_id.tg_id, text)
            await asyncio.sleep(0, 5)

        except:
            pass

    lessons_print = await session.execute(select(Lesson.name).order_by(Lesson.id))
    lessons = lessons_print.fetchall()

    result = f'\n'.join([lesson_item.name for lesson_item in lessons])

    await message.answer('Вы хотите что еще изменить?\n\n'
        f'{result} ', reply_markup=lessons_keyboard(lessons))



@rt.callback_query(F.data == 'del_lesson')
async def cmd_del_lesson_callback(callback: CallbackQuery, state: FSMContext, session):

    await callback.answer()

    lessons_print = await session.execute(select(Lesson.name).order_by(Lesson.id))
    lessons = lessons_print.fetchall()

    result = f'\n'.join([lesson_item.name for lesson_item in lessons])

    await callback.message.answer('Вот наши уроки: \n\n'
                         f'{result} ', reply_markup=lessons_keyboard(lessons))

    await state.set_state(EditLessons.del_lesson)
    await callback.message.answer('Какой урок вы хотите удалить (введите команду /end, чтобы прекратить процесс) ?')

@rt.message(EditLessons.del_lesson)
async def cmd_del_lesson_callback(message: Message, state: FSMContext, session):

    try:

        await state.update_data(del_lesson = message.text)
        lesson_del = await state.get_data()
        sel_lesson_del =  await session.execute(select(Lesson).where(Lesson.name == lesson_del['del_lesson']))

        lesson_del_db =  sel_lesson_del.scalar_one_or_none()
        print(lesson_del_db.id,lesson_del_db.name)

        if lesson_del_db == None:
            await message.answer('Такого урока нет')
        else:

            await session.delete(lesson_del_db)
            await session.commit()

            sel_users_id = await session.execute(select(User))
            users_tg_id = sel_users_id.scalars()


            text = f'Урок "{lesson_del_db.name}" удалили '

            for user_tg_id in users_tg_id:

                try:

                    await bot.send_message(user_tg_id.tg_id, text)
                    await asyncio.sleep(0,5)

                except:
                    pass

            lessons_print = await session.execute(select(Lesson.name).order_by(Lesson.id))
            lessons = lessons_print.fetchall()

            result = f'\n'.join([lesson_item.name for lesson_item in lessons])

            await message.answer('Вы хотите что еще добавить?\n\n'
                f'{result} ', reply_markup=lessons_keyboard(lessons))

    except IntegrityError:
        await message.answer('На этот урок кто то записан')

@rt.callback_query(F.data == 'reg')
async def cmd_callback_reg(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg.reg_name)
    await callback.answer()

    await callback.message.answer('Введите имя')


@rt.message(Reg.reg_name)
async def reg_name(message: Message, state: FSMContext, session):

    search_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))

    user = search_user.scalar_one_or_none()
    search_admin =  await session.execute(select(User).where(User.tg_id.in_(admins)))

    admin = search_admin.scalar_one_or_none()

    await state.update_data(name = message.text)
    name = await state.get_data()



    if user == None and message.from_user.id not in admins:

        user_add = User(tg_id = message.from_user.id,user_name = name['name'], role = 'user')
        session.add(user_add)
        await message.answer(f'Спасибо за регестрацию, {name['name']}')

        await message.answer("Что вы сегодня хотите сделать?", reply_markup=keyboard_menu())

    if admin == None:

        admin_add = User(tg_id = message.from_user.id,user_name = name['name'], role = 'admin')
        session.add(admin_add)

        await message.answer('Спасибо за регестрацию, админ')

        await message.answer("Вот ваши команды:\n"
                             "/all - посмотреть всех пользователей\n"
                             "/send_message - отправить сообщения всем пользователям\n"
                             "/edit_lessons - редактировать уроки\n"
                             "Что вы сегодня хотите сделать?", reply_markup=keyboard_menu())

    await session.commit()


@rt.callback_query(F.data == 'record_lesson')
async def cmd_record_lesson_callback(callback: CallbackQuery, state: FSMContext,session):

    await callback.answer()

    await state.set_state(RecordLesson.choose_lesson)

    lessons_print = await session.execute(select(Lesson.name).order_by(Lesson.id))
    lessons = lessons_print.fetchall()

    result = f'\n'.join([lesson_item.name for lesson_item in lessons])
    print(result)
    await callback.message.answer('Вот наши уроки: \n\n'
                         f'{result} ', reply_markup=lessons_keyboard(lessons))


@rt.message(RecordLesson.choose_lesson)
async def cmd_choose_lesson(message: Message, state: FSMContext):
    global choose_lesson

    await state.update_data(lesson = message.text)
    choose_lesson = await state.get_data()
    await message.answer('Хорошо',reply_markup=ReplyKeyboardRemove())
    await message.answer('Теперь выбирете дату ',reply_markup = await SimpleCalendar(locale='ru_RU.UTF-8').start_calendar())
    await state.set_state(RecordLesson.choose_data)

@rt.callback_query(RecordLesson.choose_data,SimpleCalendarCallback.filter())
async def process_simple_calendar(callback: CallbackQuery, callback_data:SimpleCalendarCallback, state: FSMContext):
    global choose_lesson, choose_date


    calendar = SimpleCalendar(locale='ru_RU.UTF-8')

    start_date = datetime.datetime.now()
    end_date = start_date + datetime.timedelta(days = 365)

    calendar.set_dates_range(start_date, end_date)

    is_selected, date = await calendar.process_selection(callback, callback_data)
    print(is_selected)

    if is_selected:

        date_str =  datetime.datetime.strftime(date, '%d/%m/%Y')
        await state.update_data(date = datetime.datetime.strptime(str(date_str), '%d/%m/%Y').date())
        await callback.message.delete()
        choose_date = await state.get_data()
        print(choose_date['date'],type(choose_date['date']))

        await state.set_state(RecordLesson.choose_time)
        await callback.message.answer('Введите время в формате часы:минуты , например, 14:30 ')


@rt.message(RecordLesson.choose_time)
async def cmd_choose_time(message: Message, state: FSMContext,session):
    global choose_lesson, choose_date, choose_time
    try:
        message_time = datetime.datetime.strptime(message.text, '%H:%M').time()
        print(message_time)
        await state.update_data(time = message_time)
        choose_time = await state.get_data()

    except ValueError:
        await message.answer('Введите время в формате часы:минуты , например, 14:30')


    search_user_id = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user_id = search_user_id.scalar_one()

    print(user_id)
    search_lesson_id = await session.execute(select(Lesson).where(Lesson.name == choose_lesson['lesson']))
    lesson_id = search_lesson_id.scalar_one()
    print(lesson_id)
    add_record = Record(user_id = user_id.id, lesson_id = lesson_id.id, date = choose_date['date'], time = choose_time['time'])
    session.add(add_record)
    await message.answer('Мы вас записали, не опоздайте!')

    await session.commit()
    await state.clear()

@rt.callback_query(F.data == 'look_my_lesson')
async def cmd_look_my_lesson(callback: CallbackQuery,  session , state: FSMContext):

    await callback.answer()

    search_user_id = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
    user_id = search_user_id.scalar_one_or_none()

    sel_info_record_user = await session.execute(select(Record).where(Record.user_id == user_id.id).limit(1))
    info_record_user = sel_info_record_user.scalar()

    if info_record_user == None:
        await callback.message.answer('У вас нет записей')

    else:
        search_record_user = await session.execute(select(Record).order_by(Record.id).options(joinedload(Record.lesson)).where(Record.user_id == user_id.id))
        records_user = search_record_user.scalars()
        search_data = await session.execute(select(Record).where(Record.user_id == user_id.id))
        data = search_data.scalars()
        search_time = await session.execute(select(Record).where(Record.user_id == user_id.id))
        time = search_time.scalars()
        search_records_id = await session.execute(select(Record).where(Record.user_id == user_id.id))
        records_id_bd = search_records_id.scalars()



        number = [ str(record_id.id) for record_id in records_id_bd]
        name = [str(record_name.lesson.name) for record_name in records_user]
        data = [str(data.date) for data in data]
        time = [str(time.time)[:-3] for time in time]

        data = list(zip(number, name, data, time))

        # await callback.message.answer('Вот наши уроки: \n'
        #                               f'номер:|{records_id}               |\n'
        #                               f'Урок: |{records_name}|\n '
        #                               f'дата: |{records_date} |\n'
        #                               f'время:|{records_time}              |\n')

        await callback.message.answer(f" <pre>{tabulate(data, headers=['Номер', 'Урок', 'Дата', 'Время'], tablefmt='psql', stralign='center', numalign='center')}</pre>", parse_mode='HTML')




@rt.callback_query(F.data == 'record_del_lesson')
async def cmd_callback_record_del_lesson(callback: CallbackQuery, state: FSMContext ,session):

    await state.set_state(RecordDel.number_lesson)

    await callback.answer()
    search_user_id = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
    user_id = search_user_id.scalar_one()

    sel_info_record_user = await session.execute(select(Record).where(Record.user_id == user_id.id).limit(1))
    info_record_user = sel_info_record_user.scalar_one_or_none()

    if info_record_user == None:
        await callback.message.answer('У вас нет записей')

    else:

        await cmd_look_my_lesson(callback, session, state)

        await callback.message.answer('Введите номер урока')

@rt.message(RecordDel.number_lesson)
async def cmd_record_del_lesson(message: Message, state: FSMContext, session):


    search_user_id = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user_id = search_user_id.scalar_one()



    await state.update_data(number_lesson = int(message.text))

    del_record = await state.get_data()


    sel_lessons_name = await session.execute(select(Record).options(joinedload(Record.lesson)).order_by(Record.id).where(Record.user_id == user_id.id))
    lessons_name = sel_lessons_name.scalars()

    sel_del_record = await session.execute(select(Record).options(joinedload(Record.lesson)).order_by(Record.id).where(Record.user_id == user_id.id and Record.lesson.name == lessons_name.lesson.name[del_record['number_lesson']-1]))
    del_record = sel_del_record.scalar()


    await session.delete(del_record)
    await session.commit()
    await message.answer('Урок отменен')



# @rt.message(F.text,StateFilter(None))
# async def command_text_handler(message: Message) -> None:
#         await message.answer('Нажмите на кнопки или команды, чтобы начать игру')