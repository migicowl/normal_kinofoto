from datetime import timedelta
from flask import Flask, jsonify
from flask import request as flask_request
from sys import stdout

import logging
import telebot
from telebot import types
from random import randint

from table_engine import start
import date_encode

VERSION, UPDATE_DATE = 'beta 0.1.0w', '03.02.2025'
TOKEN = '7410749887:AAFmq-H68knFTvKRyTRAsqmMQU7ONXEkNX0'
# curl -X GET https://api.telegram.org/bot7410749887:AAFmq-H68knFTvKRyTRAsqmMQU7ONXEkNX0/getWebhookInfo
# curl -X POST "https://api.telegram.org/bot7410749887:AAFmq-H68knFTvKRyTRAsqmMQU7ONXEkNX0/deleteWebhook"
# curl -X POST "https://api.telegram.org/bot7410749887:AAFmq-H68knFTvKRyTRAsqmMQU7ONXEkNX0/setWebhook?url=https://example.com/webhook"
# TOKEN = '7271784948:AAGnxoMNxOaZgBgysmChV98TA8S3lLckkpM'  # TODO debbug bot
# curl -X GET https://api.telegram.org/bot7271784948:AAGnxoMNxOaZgBgysmChV98TA8S3lLckkpM/getWebhookInfo
# curl -X POST "https://api.telegram.org/bot7271784948:AAGnxoMNxOaZgBgysmChV98TA8S3lLckkpM/deleteWebhook"
# curl -X POST "https://api.telegram.org/bot7271784948:AAGnxoMNxOaZgBgysmChV98TA8S3lLckkpM/setWebhook?url=https://example.com/webhook"
# https://kinofoto.vercel.app/webhook


# Создание логгера
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Уровень для основного логгера

# Логирование в стандартный вывод (stdout)
info_handler = logging.StreamHandler(stdout)  # Этот обработчик будет выводить логи в stdout
info_handler.setLevel(logging.INFO)  # Уровень логирования (например, INFO)
info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  # Формат логов
info_handler.setFormatter(info_formatter)  # Устанавливаем формат
logger.addHandler(info_handler)  # Добавляем обработчик в логгер

bot = telebot.TeleBot(TOKEN)


commands = [
    telebot.types.BotCommand(command="/start", description="Начать работу с ботом и обновить его"),
    telebot.types.BotCommand(command="/help", description="А что я могу?"),
    telebot.types.BotCommand(command="/version", description="Узнать версию"),
    telebot.types.BotCommand(command="/original", description="Отправить оригинал расписания"),

]
bot.set_my_commands(commands)


def log(fist_name, last_name, text, chat_id):
    logger.info(f'user: {fist_name} {last_name} text: {text} '
                f'id: {chat_id}')


# @bot.message_handler(content_types=['photo'])
# def get_photo(message):
#     bot.reply_to(message, 'Картинка!')


# @bot.message_handler(commands=['start'])
def main(chat_id, first_name, last_name):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1_1 = types.KeyboardButton('Расписание на завтра')
    btn1_2 = types.KeyboardButton('Расписание на сегодня')
    markup.row(btn1_1, btn1_2)
    btn2_1 = types.KeyboardButton('Пн')
    btn2_2 = types.KeyboardButton('Вт')
    btn2_3 = types.KeyboardButton('Ср')
    btn2_4 = types.KeyboardButton('Чт')
    btn2_5 = types.KeyboardButton('Пт')
    btn2_6 = types.KeyboardButton('Сб')
    markup.row(btn2_1, btn2_2, btn2_3, btn2_4, btn2_5, btn2_6)
    if last_name is None:
        name = f'{first_name}'
    else:
        name = f'{first_name} {last_name}'
    bot.send_message(chat_id, f'Привет, {name}\n\n/help - чтобы получить список возможностей',
                     reply_markup=markup)


help_text = '''<em>Помогите...</em>

Вводите дату через пробел (например: "10 09")
или с точкой (например: "10.09")

/original - PDF файл расписания от Рины
/start - обновление бота. Если заметите, что что-то работает не так, сначала обновите бота
/version - выводит версию бота
<code>Хочу руконожку</code> - бот пришлёт руконожку

Бот работает в очень альфа версии, работоспособность не гарантируется
Если не отвечает напишите, перезапустим
Если начнет просить доступ в браузер, <b>отключить из розетки</b>'''


# @bot.message_handler(commands=['help'])
def help_user(chat_id):
    bot.send_message(chat_id, help_text, parse_mode='html')


# @bot.message_handler(commands=['version'])
def version(chat_id):
    bot.send_message(chat_id, f'Версия бота: <em>{VERSION}</em> от <em>{UPDATE_DATE}</em>', parse_mode='html')


# @bot.message_handler(commands=['original'])
def get_original(chat_id):
    with open('./original_table.pdf', 'rb') as file:
        bot.send_document(chat_id, file)


def get_handslegs():
    meme = randint(1, 14)
    return f'./handslegs/{meme}.jpg'


def info(text, chat_id):
    if text.lower() == 'id':
        bot.send_message(chat_id, f'ID: {chat_id}')

    elif text.lower() == 'хочу руконожку':
        file = get_handslegs()
        with open(file, 'rb') as file:
            bot.send_photo(chat_id, file, caption='Руконожка живет на канале @eto_krivo')

    elif text.lower() == 'расписание на завтра':
        today = date_encode.get_moscow_tz_today()
        one_day = timedelta(days=1)
        tomorrow = today + one_day
        message_text = f'{tomorrow.day} {tomorrow.month}'
        print_data = start(message_text)
        bot.send_message(chat_id, print_data, parse_mode='html')

    elif text.lower() == 'расписание на сегодня':
        today = date_encode.get_moscow_tz_today()
        message_text = f'{today.day} {today.month}'
        print_data = start(message_text)
        bot.send_message(chat_id, print_data, parse_mode='html')

    elif text.lower() == 'вс':
        bot.send_message(chat_id, 'В воскресенье по расписанию только сон', parse_mode='html')

    elif text.lower() in date_encode.WEEKDAYS_SHORT:
        message_text = date_encode.get_weekday_data(text.lower())
        print_data = start(message_text)
        bot.send_message(chat_id, print_data, parse_mode='html')

    else:
        print_data = start(text)
        bot.send_message(chat_id, print_data, parse_mode='html')


logger.info('Bot was initializing successfully')

app = Flask(__name__)
logger.info('Flask was initializing successfully')


@app.route('/webhook', methods=['POST'])
def webhook():
    update = flask_request.get_json()
    chat_id = update['message']['chat']['id']
    message = update['message']['text']
    first_name = update['message']['from']['first_name']
    last_name = update['message']['from']['last_name']

    if '/start' == message.lower():
        main(chat_id, first_name, last_name)
    elif '/help' == message.lower():
        help_user(chat_id)
    elif '/version' == message.lower():
        version(chat_id)
    elif '/original' == message.lower():
        get_original(chat_id)
    elif 'привет' in message.lower():
        bot.send_message(chat_id, f'Ну привет, {message.from_user.first_name} {message.from_user.last_name}')
    else:
        info(message, chat_id)

    log(first_name, last_name, message, chat_id)
    return jsonify(update)


@app.route('/webhook', methods=['GET'])
def index():
    return_html = f'<h1>Server is active</h1>\n<text>status: OK</text>\n<text>version: {VERSION} {UPDATE_DATE}</text>'
    return return_html


# Запуск Flask
if __name__ == '__main__':
    logger.info('Bot is working')
    app.run()
