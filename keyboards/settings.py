from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def settings_keyboard():
    settings = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    name = KeyboardButton("Змінити ім'я")
    age = KeyboardButton("Змінити вік")
    settings.row(name, age)
    gender = KeyboardButton("Змінити гендер")
    settings.row(gender)
    back = KeyboardButton("Назад")
    settings.add(back)
    return settings
