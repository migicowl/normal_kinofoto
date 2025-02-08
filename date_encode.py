import datetime
import pytz

WEEKDAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
WEEKDAYS_SHORT = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб']


def date_format_for_search(date):
    if date[0] < 10:
        output_str = f'0{date[0]}'
    else:
        output_str = f'{date[0]}'
    if date[1] < 10:
        output_str = f'{output_str}.0{date[1]}'
    else:
        output_str = f'{output_str}.{date[1]}'
    return output_str


def get_weekday_data(weekday):
    today = datetime.date.today()
    day_of_week = today.weekday()  # Текущий день недели (0 = Понедельник, 6 = Воскресенье)
    target_day_index = WEEKDAYS_SHORT.index(weekday)  # Индекс желаемого дня недели

    days_until_target = (target_day_index - day_of_week + 7) % 7  # Количество дней до ближайшего целевого дня недели

    # Если сегодняшний день - целевой день, то сдвигаем на следующую неделю
    # if days_until_target == 0:
    #     days_until_target = 7

    target_date = today + datetime.timedelta(days=days_until_target)  # Вычисляем дату ближайшего целевого дня недели

    return f'{target_date.day} {target_date.month}'


def get_moscow_tz_today():
    server_tz = pytz.utc
    local_tz = pytz.timezone('Europe/Moscow')
    server_time = datetime.datetime.now(server_tz)
    local_time = server_time.astimezone(local_tz)
    return local_time


