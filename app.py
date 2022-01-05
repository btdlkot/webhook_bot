import os
import telebot
from telebot import types
import psycopg2
import logging
from config import *
from flask import Flask, request
from states.Questionnaire import Questions
from states.Menu import Menu
from states.Settings import Settings
from keyboards import settings, back, gender, menu
from constants import NAME, AGE, GENDER, CHANGE, NAME_VALIDATION, AGE_VALIDATION, GENDER_VALIDATION, BACK, PARAM
from validators import check_name, check_age, check_gender
from telebot import custom_filters

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()


def db_update(message):
    user_id = message.from_user.id
    with bot.retrieve_data(message.from_user.id) as data:
        name = data['name']
        age = data['age']
        gender = data['gender']
    db_object.execute(f"UPDATE users SET name = (%s), age = (%s), gender = (%s) WHERE id = {user_id}", (name, age, gender))
    db_connection.commit()


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    bot.reply_to(message, f"Привіт!\n"
                          "Для початку напишіть Ваше ім'я", reply_markup=types.ReplyKeyboardRemove(selective=False))

    db_object.execute(f"SELECT id FROM users WHERE id = {user_id}")
    result = db_object.fetchone()
    bot.set_state(message.from_user.id, Questions.Name)

    if not result:
        db_object.execute("INSERT INTO users(id, username) VALUES (%s, %s)", (user_id, username))
        db_connection.commit()
        bot.set_state(message.from_user.id, Questions.Name)


@bot.message_handler(func=lambda message: True, content_types=["text"], state=Questions.Name)
def answer_name(message):
    answer = message.text
    if check_name(answer):
        with bot.retrieve_data(message.from_user.id) as data:
            data['name'] = message.text
        bot.send_message(message.chat.id, AGE, reply_markup=back.back_keyboard())
        bot.set_state(message.from_user.id, Questions.Age)
    else:
        bot.send_message(message.chat.id, NAME_VALIDATION)


@bot.message_handler(content_types=["text"], state=Questions.Age)
def answer_age(message):
    answer = message.text
    if answer in BACK:
        bot.send_message(message.chat.id, NAME)
        bot.set_state(message.from_user.id, Questions.Name)
    else:
        if check_age(answer):
            with bot.retrieve_data(message.from_user.id) as data:
                data['age'] = message.text
            bot.send_message(message.chat.id, GENDER, reply_markup=gender.gender_keyboard())
            bot.set_state(message.from_user.id, Questions.Gender)
        else:
            bot.send_message(message.chat.id, AGE_VALIDATION)


@bot.message_handler(content_types=["text"], state=Questions.Gender)
def answer_gender(message):
    answer = message.text
    if answer in BACK:
        bot.send_message(message.chat.id, AGE)
        bot.set_state(message.from_user.id, Questions.Age)
    else:
        if check_gender(answer):
            with bot.retrieve_data(message.from_user.id) as data:
                data['gender'] = message.text
            bot.send_message(message.chat.id, "Ви пройшли анкетування", reply_markup=menu.menu_keyboard())
            db_update(message)
            bot.set_state(message.from_user.id, Menu.Menu)
        else:
            bot.send_message(message.chat.id, GENDER_VALIDATION)


@bot.message_handler(content_types=["text"], state=Menu.Menu)
def answer_main_menu(message):
    answer = message.text
    if answer in "Інфа про мене":
        with bot.retrieve_data(message.from_user.id) as data:
            bot.send_message(message.chat.id,
                             "\n<b>Ім'я: {name}\nВік: {age}\nГендер: {gender}</b>".format(
                                 name=data['name'], age=data['age'], gender=data['gender']), parse_mode="html")
    elif answer in "Налаштування":
        bot.send_message(message.chat.id, PARAM,
                         reply_markup=settings.settings_keyboard())
        bot.set_state(message.from_user.id, Settings.Main)
    elif answer in BACK:
        bot.send_message(message.chat.id, GENDER, reply_markup=gender.gender_keyboard())
        bot.set_state(message.from_user.id, Questions.Gender)
    else:
        bot.send_message(message.chat.id, "Потрібно обрати один з варіантів меню")


@bot.message_handler(content_types=["text"], state=Settings.Main)
def answer_settings(message):
    answer = message.text
    if answer in "Змінити ім'я":
        bot.send_message(message.chat.id, CHANGE, reply_markup=back.back_keyboard())
        bot.set_state(message.from_user.id, Settings.Change_name)
    elif answer in "Змінити вік":
        bot.send_message(message.chat.id, CHANGE, reply_markup=back.back_keyboard())
        bot.set_state(message.from_user.id, Settings.Change_age)
    elif answer in "Змінити гендер":
        bot.send_message(message.chat.id, CHANGE, reply_markup=gender.gender_keyboard())
        bot.set_state(message.from_user.id, Settings.Change_gender)
    elif answer in BACK:
        bot.send_message(message.chat.id, "Meню: ", reply_markup=menu.menu_keyboard())
        bot.set_state(message.from_user.id, Menu.Menu)
    else:
        bot.send_message(message.chat.id, "Потрібно обрати один з варіантів меню")


@bot.message_handler(content_types=["text"], state=Settings.Change_name)
def answer_change_name(message):
    answer = message.text
    if answer in BACK:
        bot.send_message(message.chat.id, PARAM, reply_markup=settings.settings_keyboard())
        bot.set_state(message.from_user.id, Settings.Main)
    elif check_name(answer):
        with bot.retrieve_data(message.from_user.id) as data:
            data['name'] = message.text
        bot.send_message(message.chat.id, "Ім'я зменено на " + answer, reply_markup=menu.menu_keyboard())
        db_update(message)
        bot.set_state(message.from_user.id, Menu.Menu)
    else:
        bot.send_message(message.chat.id, NAME_VALIDATION)


@bot.message_handler(content_types=["text"], state=Settings.Change_age)
def answer_change_age(message):
    answer = message.text
    if answer in BACK:
        bot.send_message(message.chat.id, PARAM, reply_markup=settings.settings_keyboard())
        bot.set_state(message.from_user.id, Settings.Main)
    elif check_age(answer):
        with bot.retrieve_data(message.from_user.id) as data:
            data['age'] = message.text
        bot.send_message(message.chat.id, "Вік зменено на " + answer, reply_markup=menu.menu_keyboard())
        db_update(message)
        bot.set_state(message.from_user.id, Menu.Menu)
    else:
        bot.send_message(message.chat.id, AGE_VALIDATION)


@bot.message_handler(content_types=["text"], state=Settings.Change_gender)
def answer_change_gender(message):
    answer = message.text
    if answer in BACK:
        bot.send_message(message.chat.id, PARAM, reply_markup=settings.settings_keyboard())
        bot.set_state(message.from_user.id, Settings.Main)
    elif check_gender(answer):
        with bot.retrieve_data(message.from_user.id) as data:
            data['gender'] = message.text
        bot.send_message(message.chat.id, "Гендер зменено на " + answer, reply_markup=menu.menu_keyboard())
        db_update(message)
        bot.set_state(message.from_user.id, Menu.Menu)
    else:
        bot.send_message(message.chat.id, GENDER_VALIDATION)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())


@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def redirect_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
