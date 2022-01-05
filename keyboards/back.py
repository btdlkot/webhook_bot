from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def back_keyboard():
    back = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item = KeyboardButton("Назад")
    back.add(item)
    return back
