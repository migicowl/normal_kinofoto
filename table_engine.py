import datetime
import date_encode
import database

LESSON_TIME = {0: '8:30 - 10:00', 1: '10:10 - 11:40', 2: '12:10 - 13:40', 3: '13:50 - 15:20', 4: '15:30 - 17:00',
               5: '17:10 - 18:40', 6: '18:50 - 20:20', 7: '20:30 - 22:00'}
WEEKDAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']


class DateEngineError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def date_engine(user_date):
    # require '01 09' or '01.09' format
    value = []

    if '.' in user_date:
        user_date = user_date.split('.')
    else:
        user_date = user_date.split(' ')

    if len(user_date) != 2:
        raise DateEngineError(f'\n\nВероятно вы ввели данные без пробела/точки или больше двух чисел\n\n '
                              f'<code>Ошибка в списке {user_date}</code>')

    for i in user_date:
        if i.isdigit():
            i = int(i)
            value.append(i)
        else:
            raise DateEngineError(f'Это не целое число "{i}",\n\n<code>индекс в списке {user_date.index(i)}</code>')

    try:
        date = datetime.date(year=datetime.datetime.now().year, day=int(value[0]), month=int(value[1]))
    except ValueError as e:
        raise DateEngineError(f'Ошибка в введённых значениях дня или месяца\n\n<code>({e})</code>')

    if date.weekday() == 6:
        raise DateEngineError('Вы выбрали воскресенье. В воскресенье спим')

    return value, date.weekday()


def table_engine(raw_table, user_date):
    table = []

    for lesson_number, lesson_area in raw_table.items():
        # duble_chek = False

        # lesson_number = номер пары (int), lesson_area = название пары: [даты] (dict)
        if len(lesson_area) == 0:
            table.append([lesson_number, "Ничего"])
            continue
        for lesson_name, lesson_value in lesson_area.items():
            # if duble_chek:
            #     continue
            if user_date in lesson_value:
                table.append([lesson_number, lesson_name])
            else:
                if len(lesson_area) == 1:
                    table.append([lesson_number, "Ничего"])
                # table.append([lesson_number, "Ничего"])
                # duble_chek = True

    return table


def table_print_engine(prepare_table, user_data, weekday):
    print_text = f'РАСПИСАНИЕ НА ДАТУ {user_data}\n<em>{WEEKDAYS[weekday]}</em> \n'
    for number, name in prepare_table:
        print_text += '\n' + f'{LESSON_TIME[number]}' + '\n' + f'<b>{name}</b>' + '\n'

    return print_text


def start(message_text):
    try:
        user_date, weekday = date_engine(message_text)
    except DateEngineError as e:
        output_print = f'Произошла ошибочка: <em>{e}</em>'
    else:
        user_date = date_encode.date_format_for_search(user_date)
        table = table_engine(database.main_base[weekday], user_date)
        output_print = table_print_engine(table, user_date, weekday)

    return output_print
