from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def gender_keyboard():
    gender = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    w = KeyboardButton("Жінка")
    m = KeyboardButton("Чоловік")
    gender.row(w, m)
    back = KeyboardButton("Назад")
    gender.add(back)
    return gender
