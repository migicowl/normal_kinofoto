from logger import debug_log, message_log

from datetime import timedelta
from random import randint
from supabase import create_client, Client

import telebot

import date_encode
from table_engine import start

debug_log('bot_engine was initializing')

VERSION, UPDATE_DATE, TABLE_UPDATE_DATE = 'beta 0.2.0w', '06.02.2025', '30.01.2025'

# TOKEN = '7410749887:AAFmq-H68knFTvKRyTRAsqmMQU7ONXEkNX0'
# TOKEN = '7271784948:AAGnxoMNxOaZgBgysmChV98TA8S3lLckkpM'  # TODO debbug bot
TOKEN = '7845300949:AAFt7NfYGGf6m10lGTOrrYlaDstfHh1qIgg'  # TODO debbug2 bot

help_text = '''<em>Помогите...</em>

Вводите дату через пробел (например: "10 09")
или с точкой (например: "10.09")

/original - PDF файл расписания от Рины
/start - обновление бота. Если заметите, что что-то работает не так, сначала обновите бота
/version - выводит версию бота
<code>Хочу руконожку</code> - бот пришлёт руконожковый совет

Бот работает в очень альфа версии, работоспособность не гарантируется
Если не отвечает напишите, перезапустим
Если начнет просить доступ в браузер, <b>отключить из розетки</b>'''

bot = telebot.TeleBot(TOKEN)

commands = [
    telebot.types.BotCommand(command="/help", description="А что я могу?"),
    telebot.types.BotCommand(command="/start", description="Начать работу с ботом и обновить его"),
    telebot.types.BotCommand(command="/course", description="Выбрать свой курс [beta]"),
    telebot.types.BotCommand(command="/original", description="Отправить оригинал расписания"),
    telebot.types.BotCommand(command='/table_ver', description="Когда обновлялось расписание"),
    telebot.types.BotCommand(command="/version", description="Узнать версию бота"),
]
bot.set_my_commands(commands)

url_supbase = "https://ftsuuladorswyeuijota.supabase.co"  # URL проекта
key_supbase = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ0c3V1bGFkb3Jzd3lldWlqb3RhIiwic" \
              "m9sZSI6ImFub24iLCJpYXQiOjE3Mzg3ODU5MzYsImV4cCI6MjA1NDM2MTkzNn0.MVpztnP2_XNTHV3hhl-NQm-w_" \
              "4o8BbCZMwiK3q7doeI"  # Ключ API, полученный на Supabase
# url_supbase = environ.get('url_supbase')
# key_supbase = environ.get('key_supbase')
supabase: Client = create_client(url_supbase, key_supbase)


@bot.message_handler(commands=['start'])
def main(message):
    debug_log('Main is triggered')
    debug_log(message)
    markup_main = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1_1 = telebot.types.KeyboardButton('Через неделю')
    btn1_2 = telebot.types.KeyboardButton('Расписание на завтра')
    btn1_3 = telebot.types.KeyboardButton('Расписание на сегодня')
    markup_main.row(btn1_2, btn1_3)
    btn2_1 = telebot.types.KeyboardButton('Пн')
    btn2_2 = telebot.types.KeyboardButton('Вт')
    btn2_3 = telebot.types.KeyboardButton('Ср')
    btn2_4 = telebot.types.KeyboardButton('Чт')
    btn2_5 = telebot.types.KeyboardButton('Пт')
    btn2_6 = telebot.types.KeyboardButton('Сб')
    markup_main.row(btn2_1, btn2_2, btn2_3, btn2_4, btn2_5, btn2_6)
    if message.from_user.last_name is None:
        name = f'{message.from_user.first_name}'
    else:
        name = f'{message.from_user.first_name} {message.from_user.last_name}'
    bot.send_message(message.chat.id,
                     f'Привет, {name}\n\n/help - чтобы получить список возможностей\n\nВводи дату в формате 12.01 или '
                     f'12 01\n\nВАЖНО!!\nВыбери курс используя команду /course\nПо умолчанию расписание выдаётся '
                     f'для третьего курса\n\nБот работает в альфа версии\nНапиши "<code>Хочу руконожку</code>" и бот '
                     f'пришлёт руконожковый совет',
                     reply_markup=markup_main, parse_mode='html')
    message_log(message)


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    bot.reply_to(message, 'Картинка!')


@bot.message_handler(commands=['help'])
def help_user(message):
    debug_log('help_user triggered')
    bot.send_message(message.chat.id, help_text, parse_mode='html')
    message_log(message)


@bot.message_handler(commands=['course'])
def get_course(message):
    markup_course = telebot.types.InlineKeyboardMarkup()  # Используем InlineKeyboardMarkup для прикрепленных кнопок
    btn1 = telebot.types.InlineKeyboardButton('1 курс', callback_data='course_1')
    btn2 = telebot.types.InlineKeyboardButton('2 курс', callback_data='course_2')
    btn3 = telebot.types.InlineKeyboardButton('3 курс', callback_data='course_3')
    btn4 = telebot.types.InlineKeyboardButton('4 курс', callback_data='course_4')
    markup_course.row(btn1, btn2, btn3, btn4)

    bot.send_message(message.chat.id, 'Укажите курс для которого вы хотите получать расписание',
                     reply_markup=markup_course)
    message_log(message)


def change_course(text, chat_id):
    if text not in ['1', '2', '3', '4']:
        return False

    try:
        # Обновляем или вставляем курс
        supabase.from_('user_courses').upsert({
            'id': chat_id,
            'course': text
        }).execute()
    except Exception as e:
        debug_log(f'Change_course raise: {e}')

    debug_log('Course was changed')
    return True


def find_course(chat_id):
    debug_log(f'find_course is triggered')

    try:
        debug_log(f'we in try. chat_id {chat_id}')
        data = supabase.from_('user_courses').select('course').eq('id', str(chat_id)).execute()
        debug_log(f'data: {data}')
        data = data.data[0]['course']
        debug_log(f"find_course return {data}")
        if data.data:
            return data
    except Exception as e:
        debug_log(f'Find_course raise: {e}')
        return '3'

    return '3'


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    debug_log('handle_query is triggered')

    if call.data.startswith('course_'):

        course_number = call.data[-1]  # Получаем номер курса из callback_data
        if change_course(text=course_number, chat_id=call.message.chat.id):
            # Редактируем текст сообщения
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f'Спасибо. Я запомню что вы на {find_course(call.message.chat.id)} курсе',
                parse_mode='html'
            )

        else:
            error_text = 'Мне жаль, но что-то пошло не так\n\nПопробуйте снова\n\n' \
                         'Если ошибка повторится, обратитесь в поддержку '
            bot.send_message(call.message.chat.id, error_text, parse_mode='html')

        # Убираем кнопки из сообщения
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )

        # Отправляем ответ, чтобы кнопка больше не мигала
        bot.answer_callback_query(call.id, text=f' ', show_alert=False)


@bot.message_handler(commands=['table_ver'])
def table_ver(message):
    bot.send_message(message.chat.id, f'Последнее обновление расписания было {TABLE_UPDATE_DATE}', parse_mode='html')
    message_log(message)


@bot.message_handler(commands=['version'])
def version(message):
    bot.send_message(message.chat.id, f'Версия бота: <em>{VERSION}</em> от <em>{UPDATE_DATE}</em>', parse_mode='html')
    message_log(message)


@bot.message_handler(commands=['original'])
def get_original(message):
    with open('./original_table.pdf', 'rb') as file:
        bot.send_document(message.chat.id, file)
    message_log(message)


@bot.message_handler(commands=['debuginfo'])
def debug_info(message):
    bot.send_message(message.chat.id, f'Временно отключено')
    message_log(message)


def get_handslegs():
    meme = randint(1, 16)
    return f'./handslegs/{meme}.jpg'


@bot.message_handler()
def info(message):
    debug_log('info is triggered')
    debug_log(f'ID: {message.chat.id}')
    debug_log(f'TEXT: {message.text}')
    debug_log(f'TEXT lower: {message.text.lower()}')

    if message.text.lower() == 'id':
        bot.send_message(message.chat.id, f'ID: <em>{message.chat.id}</em>', parse_mode='html')

    elif message.text.lower() == 'хочу руконожку':
        file = get_handslegs()
        with open(file, 'rb') as file:
            bot.send_photo(message.chat.id, file, caption='Руконожка живет на канале @eto_krivo')

    elif message.text.lower() == 'расписание на завтра':
        today = date_encode.get_moscow_tz_today()
        one_day = timedelta(days=1)
        tomorrow = today + one_day
        message_text = f'{tomorrow.day} {tomorrow.month}'
        print_data = start(message_text, course=find_course(message.chat.id))
        bot.send_message(message.chat.id, print_data, parse_mode='html')

    elif message.text.lower() == 'расписание на сегодня':
        debug_log('расписание на сегодня is triggered')
        try:
            debug_log('We are in try')
            today = date_encode.get_moscow_tz_today()
            debug_log(today)
        except Exception as e:
            debug_log(f'gettoday raise error:')
            debug_log(f'gettoday raise error: {e}')
        debug_log(f'today: {today}')
        message_text = f'{today.day} {today.month}'
        debug_log(message_text)
        course = find_course(message.chat.id)
        debug_log(f'course: {course}')
        print_data = start(message_text, course=course)
        debug_log(print_data)
        bot.send_message(message.chat.id, print_data, parse_mode='html')

    elif message.text.lower() == 'через неделю':
        pass

    elif message.text.lower() == 'вс':
        bot.send_message(message.chat.id, 'В воскресенье по расписанию только сон', parse_mode='html')

    elif message.text.lower() in date_encode.WEEKDAYS_SHORT:
        message_text = date_encode.get_weekday_data(message.text.lower())
        print_data = start(message_text, course=find_course(message.chat.id))
        bot.send_message(message.chat.id, print_data, parse_mode='html')

    else:
        print_data = start(message.text, course=find_course(message.chat.id))
        bot.send_message(message.chat.id, print_data, parse_mode='html')

    message_log(message)


def bot_start(json_str):
    update = telebot.types.Update.de_json(json_str)  # Преобразуем данные в объект Update
    debug_log(update)
    bot.process_new_updates([update])  # Обрабатываем обновление
