from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def menu_keyboard():
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    info = KeyboardButton("Інфа про мене")
    settings = KeyboardButton("Налаштування")
    menu.row(info, settings)
    back = KeyboardButton("Назад")
    menu.add(back)
    return menu
