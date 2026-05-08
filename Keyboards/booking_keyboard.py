from aiogram.utils.keyboard import ReplyKeyboardBuilder,InlineKeyboardBuilder

def keyboard_menu():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='Записаться на занятие',callback_data='record_lesson')
    keyboard.button(text='Мои записи',callback_data='look_my_lesson')
    keyboard.button(text='Отменить запись', callback_data='record_del_lesson')

    keyboard.adjust(1,1,1)

    return keyboard.as_markup()

def lessons_keyboard(lessons):
    keyboard = ReplyKeyboardBuilder()
    for item in lessons:
        for lesson in item:
            print(lesson)
            keyboard.button(text=lesson)

    keyboard.adjust(2)

    return keyboard.as_markup()

def edit_lessons_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='Добавить урок', callback_data='add_lesson')
    keyboard.button(text='Изменить урок', callback_data='upd_lesson')
    keyboard.button(text='Удалить урок' , callback_data='del_lesson')

    keyboard.adjust(1,1,1)

    return keyboard.as_markup()