import sqlite3
import telebot
from telebot import types

from config import TOKEN
from db import add_user, get_all_commands, get_all_stations, get_command_id_by_name, get_user_by_username, \
    update_user_command, get_command_info, format_command_info, get_balance, get_user_command_id, get_command_name_by_id, \
    transfer_balance, admin_transfer_balance, buy_stocks, get_station_by_stationcode, get_all_stationscode,\
    get_available_stocks, sell_stocks, get_user_stocks, transfer_stocks, add_command, remove_command, \
    update_stock_price, get_station_cost

commands = get_all_commands()
bot = telebot.TeleBot(TOKEN)
stations = get_all_stations()
# Список ID администраторов
me = 562533452
admins = []
MAIN_ADMINS = []
# Глобальный словарь для хранения контекста пользователей
user_contexts = {}

# Функция для создания меню пользователя
def user_action_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Команда', 'Баланс', 'Акции')
    return markup


# Функция для создания меню администратора
def admin_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Переводы_акций', 'Главное меню')
    return markup


# Функция для создания меню выбора действия (перевод и т.д.)
def action_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Перевод', 'Главное меню')
    return markup


# Функция для создания главного меню
def main_menu(chat_id):
    markup = user_action_menu()
    bot.send_message(chat_id, 'Главное меню:', reply_markup=markup)

def balance_action_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Перевод', 'Главное меню')
    return markup

def action_action_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Перевод_акций', 'Главное меню')
    return markup

def user_action_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Команда', 'Баланс', 'Акции')
    return markup

# Функция для создания меню администратора
def admin_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Переводы', 'Главное меню')
    return markup

def fei_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Купить акции','Продать акции', 'Главное меню')
    return markup

# Функция для создания меню главного администратора
def EMPEROR_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Добавить команду','Удалить команду', 'Редактировать баланс', 'Изменить акции', 'Изменить акции%', 'Главное меню', 'Убить человека')
    return markup

# Функция для создания меню выбора действия (перевод и т.д.)
def action_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Перевод', 'Главное меню')
    return markup

def get_all_commands() -> list:
    """
    Получает список всех команд из базы данных.

    Returns:
        Список названий команд
    """
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name_command FROM commands")
        commands = [row[0] for row in cursor.fetchall()]
        return commands

    except sqlite3.Error as e:
        print(f"Ошибка при получении списка команд: {e}")
        return []

    finally:
        conn.close()


# Хендлер для команды /start
# Хендлер для команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    if not username:
        username = f"user_{user_id}"

    # Check if user already exists in the database
    user_info = get_user_by_username(username)

    if message.from_user.id in admins:
        stations = get_all_stations()
        # Если пользователь админ, показываем список станций
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for station in stations:
            item = types.KeyboardButton(station)
            markup.add(item)
        markup.add('Главное меню')
        bot.send_message(message.chat.id, 'Выберите станцию:', reply_markup=markup)
        # Регистрируем обработчик выбора станции
        bot.register_next_step_handler(message, process_station_selection)
    elif message.from_user.id in MAIN_ADMINS:
        bot.send_message(message.chat.id, 'Ваше святейшество:', reply_markup=EMPEROR_menu())
    elif user_info:
        # User already exists, show main menu instead of team selection
        command_id = user_info[1]  # Assuming user_info returns (user_id, username, command_id)
        command_name = get_command_name_by_id(command_id)
        bot.send_message(message.chat.id,
                         f"Вы уже зарегистрированы в команде '{command_name}'. Изменение команды невозможно.")
        main_menu(message.chat.id)
    else:
        # Если пользователь не админ, показываем список команд из базы данных
        commands = get_all_commands()

        if not commands:
            bot.send_message(message.chat.id,
                             'В базе данных нет доступных команд. Пожалуйста, обратитесь к администратору.')
            return

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for command in commands:
            item = types.KeyboardButton(command)
            markup.add(item)
        markup.add('Главное меню')
        bot.send_message(message.chat.id, 'Выберите команду:', reply_markup=markup)
        # Регистрируем следующий шаг - обработка выбора команды
        bot.register_next_step_handler(message, process_command_selection)


# Обработчик выбора станции администратором
def process_station_selection(message):
    if message.text == 'Главное меню':
        main_menu(message.chat.id)
        return

    station_name = message.text
    station_id = get_station_id_by_name(station_name)

    if not station_id:
        bot.send_message(message.chat.id, 'Станция не найдена. Пожалуйста, выберите станцию из списка.')
        start(message)
        return

    # Сохраняем выбор станции администратора
    save_admin_station(message.from_user.id, station_id)
    if station_name == 'Биржа':
        bot.send_message(message.chat.id, f'Вы выбрали станцию: {station_name}', reply_markup=fei_menu())
    else:
        bot.send_message(message.chat.id, f'Вы выбрали станцию: {station_name}', reply_markup=admin_menu())


# Функция для сохранения выбранной станции администратора
def save_admin_station(admin_id, station_id):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    # Проверяем, есть ли уже запись для этого админа
    cursor.execute('SELECT admin_id FROM admin_current_station WHERE admin_id = ?', (admin_id,))
    existing = cursor.fetchone()

    if existing:
        # Обновляем существующую запись
        cursor.execute('UPDATE admin_current_station SET station_id = ? WHERE admin_id = ?',
                       (station_id, admin_id))
    else:
        # Создаем новую запись
        cursor.execute('INSERT INTO admin_current_station (admin_id, station_id) VALUES (?, ?)',
                       (admin_id, station_id))

    conn.commit()
    conn.close()


# Функция для получения ID станции по её имени
def get_station_id_by_name(station_name):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    cursor.execute('SELECT station_id FROM stations WHERE name = ?', (station_name,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


# Функция для получения текущей станции администратора
def get_current_station(admin_id):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    cursor.execute('SELECT station_id FROM admin_current_station WHERE admin_id = ?', (admin_id,))
    result = cursor.fetchone()

    conn.close()

    if not result:
        return None

    return result[0]
def process_command_selection(message):
    selected_command = message.text
    # Получаем список команд из базы данных
    commands = get_all_commands()

    # Проверяем, что выбор не "Главное меню"
    if selected_command == 'Главное меню':
        # Возвращаемся в главное меню
        main_menu(message.chat.id)
        return

    # Проверяем, что выбранная команда существует в списке команд
    if selected_command in commands:
        try:
            # Находим ID команды по её названию
            command_id = get_command_id_by_name(selected_command)

            if command_id:
                # Получаем имя пользователя (или используем username из Telegram)
                username = message.from_user.username
                if not username:
                    username = f"user_{message.from_user.id}"

                # Проверяем, существует ли пользователь уже в базе
                user_info = get_user_by_username(username)

                if user_info:
                    # Пользователь существует, обновляем его команду
                    user_id = user_info[0]
                    update_user_command(user_id, command_id)
                    bot.send_message(message.chat.id, f"Вы успешно присоединились к команде '{selected_command}'!")
                else:
                    # Пользователь не существует, добавляем нового
                    user_id = add_user(username, command_id)
                    bot.send_message(message.chat.id,
                                     f"Вы успешно зарегистрированы и присоединились к команде '{selected_command}'!")

                # После регистрации показываем главное меню
                main_menu(message.chat.id)
            else:
                bot.send_message(message.chat.id, "Выбранная команда не найдена в базе данных.")

        except Exception as e:
            bot.send_message(message.chat.id, f"Произошла ошибка при выборе команды: {str(e)}")

    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите команду из предложенных вариантов.")
        # Снова отправляем клавиатуру с командами
        start(message)

def start_message(message):
    conn = sqlite3.connect('game.db')
    cur = conn.cursor()

# Хендлер для выбора команды (для пользователей)
@bot.message_handler(func=lambda message: message.text in commands)
def user_command(message):
    selected_command = message.text
    bot.send_message(message.chat.id, f'Вы выбрали команду: {selected_command}')

    # После выбора команды показываем дополнительные кнопки
    bot.send_message(message.chat.id, 'Что бы вы хотели сделать?', reply_markup=user_action_menu())

# Хендлер для выбора действия внутри "Баланс"
@bot.message_handler(func=lambda message: message.text == 'Баланс')
def balance_handler(message):
    bot.send_message(message.chat.id, f'Вы выбрали: {message.text}')

    # Получаем username пользователя
    username = message.from_user.username
    if not username:
        username = f"user_{message.from_user.id}"

    # Получаем информацию о пользователе
    user_info = get_user_by_username(username)

    if user_info:
        # Получаем ID команды пользователя
        user_id = user_info[0]
        command_id = get_user_command_id(user_id)

        if command_id:
            # Получаем баланс команды
            balance = get_balance(command_id)

            if balance is not None:
                # Получаем название команды
                command_name = get_command_name_by_id(command_id)
                bot.send_message(message.chat.id, f'Текущий баланс команды "{command_name}": {balance} монет')
            else:
                bot.send_message(message.chat.id, 'Не удалось получить баланс команды.')
        else:
            bot.send_message(message.chat.id, 'Вы не состоите в команде.')
    else:
        bot.send_message(message.chat.id,
                         'Вы не зарегистрированы в системе. Пожалуйста, выберите команду в главном меню.')

    # Показываем меню действий с балансом
    bot.send_message(message.chat.id, f'Что бы вы хотели сделать с балансом?', reply_markup=balance_action_menu())

# Хендлер для выбора действия внутри "Акции"
@bot.message_handler(func=lambda message: message.text == 'Акции')
def balance_or_promotions(message):
    bot.send_message(message.chat.id, f'Вы выбрали: {message.text}')
    user_id, command_id = get_user_by_username(message.from_user.username)
    res = get_user_stocks(user_id)
    message_text = ''
    for i in res:
        message_text += f"{i['code']}: {i['amount']}\n"
    if res ==[]:
        bot.send_message(message.chat.id, f'На вашем щету нет акций', reply_markup=action_action_menu())
    else:
        bot.send_message(message.chat.id, f'Ваши акции:\n{message_text}', reply_markup=action_action_menu())


#TODO:
# Хендлер для действия "Перевод" (для пользователей)

# Хендлер для действия "Перевод"
@bot.message_handler(func=lambda message: message.text == 'Перевод')
def transfer(message):
    commands = get_all_commands()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for command in commands:
        item = types.KeyboardButton(command)
        markup.add(item)
    markup.add('Главное меню')
    bot.send_message(message.chat.id, 'Выберете команду для перевода валюты', reply_markup = markup)
    bot.register_next_step_handler(message, money_transfer_value)
def money_transfer_value(message):
    command = message.text
    if command not in commands:
        bot.send_message(message.chat.id, 'К сожалению такой команды несуществует')
        main_menu(message.chat.id)
        return
    bot.send_message(message.chat.id, 'Введите сумму перевода:')
    bot.register_next_step_handler(message, money_transfer, command = command)
def money_transfer(message, command):
    try:
        command_to = get_command_id_by_name(command)
        amout = int(message.text)
        if amout < 0:
            bot.send_message(message.chat.id, f'Так не получится', reply_markup=user_action_menu())
            return
        user_data = get_user_by_username(message.from_user.username)
        user_id, command_id = user_data

        transfer = transfer_balance(command_id, command_to, amout)
        if not transfer:
            bot.send_message(message.chat.id, f'Ошибка при переводе', reply_markup=user_action_menu())
        else:
            bot.send_message(message.chat.id, f'Перевод выполнен!', reply_markup=user_action_menu())
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, f'Упс, что-то пошло не так', reply_markup=user_action_menu())

@bot.message_handler(func=lambda message: message.text == 'Перевод_акций')
def transfer(message):
    bot.send_message(message.chat.id, 'Введите: Имя пользователя, название станции, количество акций для перевода')
    bot.register_next_step_handler(message, action_transfer)
def action_transfer(message):
    try:

        message_vals = message.text.split(",")
        if len(message_vals) != 3:
            bot.send_message(message.chat.id, f'Возможно вы ввели команду непраивльно. Пример "Sir_Sinion, МФ, 2"', reply_markup=user_action_menu())
            return
        from_user, command_id = get_user_by_username(message.from_user.username)
        user_to, command_id = get_user_by_username(message_vals[0])
        station = message_vals[1].strip()
        station_id = get_station_by_stationcode(station)
        amount = int(message_vals[2])
        transfer = transfer_stocks(from_user, user_to, station_id, amount)
        if not transfer:
            bot.send_message(message.chat.id, f'Ошибка при переводе', reply_markup=user_action_menu())
        else:
            bot.send_message(message.chat.id, f'Перевод выполнен!', reply_markup=user_action_menu())
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, f'Упс, что-то пошло не так', reply_markup=user_action_menu())

# Хендлер для действия "Переводы" (для администраторов)
@bot.message_handler(func=lambda message: message.text == 'Переводы')
def admin_transfer(message):
    if message.chat.id not in admins:
        main_menu(message.chat.id)
        return

    # Проверяем, выбрана ли станция у администратора
    station_id = get_current_station(message.from_user.id)

    if not station_id:
        # Если станция не выбрана, предлагаем выбрать
        stations = get_all_stations()
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for station in stations:
            markup.add(types.KeyboardButton(station))
        markup.add('Главное меню')

        bot.send_message(message.chat.id, 'Сначала выберите станцию:', reply_markup=markup)
        bot.register_next_step_handler(message, process_station_for_transfer)
        return

    # Если станция выбрана, показываем список команд для перевода
    show_transfer_commands(message)


# Обработчик выбора станции для перевода
def process_station_for_transfer(message):
    if message.text == 'Главное меню':
        main_menu(message.chat.id)
        return

    station_name = message.text
    station_id = get_station_id_by_name(station_name)

    if not station_id:
        bot.send_message(message.chat.id, 'Станция не найдена. Пожалуйста, выберите станцию из списка.')
        admin_transfer(message)
        return

    # Сохраняем выбор станции администратора
    save_admin_station(message.from_user.id, station_id)

    # Показываем список команд для перевода
    show_transfer_commands(message)


# Показ списка команд для перевода
def show_transfer_commands(message):
    # Получаем список всех команд
    commands = get_all_commands()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

    # Добавляем кнопки для каждой команды
    for command in commands:
        markup.add(types.KeyboardButton(command))

    markup.add('Главное меню')
    bot.send_message(message.chat.id, 'Выберите команду для перевода валюты:', reply_markup=markup)
    bot.register_next_step_handler(message, select_transfer_amount)


# Функция выбора суммы перевода
def select_transfer_amount(message):
    if message.text == 'Главное меню':
        main_menu(message.chat.id)
        return

    command = message.text

    # Проверяем, существует ли такая команда
    if command not in get_all_commands():
        bot.send_message(message.chat.id, 'К сожалению, такой команды не существует')
        main_menu(message.chat.id)
        return

    # Создаем клавиатуру с предустановленными суммами
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

    # Стандартные суммы для перевода
    amounts = [100, 200, 300, 500, 1000]

    # Создаем кнопки по 3 в ряд
    row = []
    for i, amount in enumerate(amounts):
        row.append(types.KeyboardButton(str(amount)))
        if len(row) == 3 or i == len(amounts) - 1:
            markup.add(*row)
            row = []

    # Добавляем кнопку "Другая сумма"
    markup.add(types.KeyboardButton("Другая сумма"))
    markup.add(types.KeyboardButton("Главное меню"))

    # Сохраняем выбранную команду в контексте пользователя
    user_context = {
        'selected_command': command
    }

    # Сохраняем контекст пользователя
    user_contexts[message.from_user.id] = user_context

    bot.send_message(message.chat.id, f'Выберите сумму для перевода команде "{command}":', reply_markup=markup)
    bot.register_next_step_handler(message, process_transfer_amount)


# Обработка выбранной суммы
def process_transfer_amount(message):
    if message.text == 'Главное меню':
        main_menu(message.chat.id)
        return

    # Получаем сохраненный контекст пользователя
    user_context = user_contexts.get(message.from_user.id, {})
    command = user_context.get('selected_command')

    if not command:
        bot.send_message(message.chat.id, 'Произошла ошибка. Пожалуйста, начните заново.')
        main_menu(message.chat.id)
        return

    if message.text == "Другая сумма":
        bot.send_message(message.chat.id, 'Введите сумму перевода:')
        bot.register_next_step_handler(message, process_custom_amount)
        return

    try:
        amount = int(message.text)
        process_final_transfer(message, command, amount)
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите корректную сумму.')
        admin_transfer(message)


# Обработка пользовательской суммы
def process_custom_amount(message):
    try:
        amount = int(message.text)

        # Получаем сохраненный контекст пользователя
        user_context = user_contexts.get(message.from_user.id, {})
        command = user_context.get('selected_command')

        if not command:
            bot.send_message(message.chat.id, 'Произошла ошибка. Пожалуйста, начните заново.')
            main_menu(message.chat.id)
            return

        process_final_transfer(message, command, amount)
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите корректное число.')
        admin_transfer(message)


# Выполнение перевода с учетом контрольного пакета акций
def process_final_transfer(message, command, amount):
    try:
        command_to = get_command_id_by_name(command)

        # Получаем текущую станцию администратора
        station_id = get_current_station(message.from_user.id)

        if not station_id:
            bot.send_message(message.chat.id, 'Ошибка: не удалось определить текущую станцию.')
            main_menu(message.chat.id)
            return

        # Проверяем, есть ли команда с контрольным пакетом акций (51+)
        majority_owner = get_majority_owner_for_station(station_id)

        if majority_owner and majority_owner['command_id'] != command_to:
            # Рассчитываем 10% для владельца контрольного пакета
            majority_share = int(amount * 0.1)
            # Корректируем сумму для целевой команды
            transfer_amount = amount - majority_share

            # Перевод целевой команде
            transfer = admin_transfer_balance(command_to, transfer_amount, 0)

            # Перевод 10% владельцу контрольного пакета
            majority_transfer = admin_transfer_balance(majority_owner['command_id'], majority_share, 0)

            if not transfer or not majority_transfer:
                bot.send_message(message.chat.id, f'Ошибка при переводе', reply_markup=admin_menu())
            else:
                bot.send_message(message.chat.id,
                                 f'Перевод выполнен! {transfer_amount} переведено команде {command}.\n'
                                 f'{majority_share} (10%) отправлено команде {majority_owner["name"]} '
                                 f'как владельцу контрольного пакета акций станции.',
                                 reply_markup=admin_menu())
        else:
            # Обычный перевод без владельца контрольного пакета
            transfer = admin_transfer_balance(command_to, amount, 0)
            if not transfer:
                bot.send_message(message.chat.id, f'Ошибка при переводе', reply_markup=admin_menu())
            else:
                bot.send_message(message.chat.id, f'Перевод выполнен! {amount} переведено команде {command}.',
                                 reply_markup=admin_menu())
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, f'Упс, что-то пошло не так: {str(e)}',
                         reply_markup=admin_menu())


# Функция для получения команды с контрольным пакетом акций для станции
def get_majority_owner_for_station(station_id):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    # Получаем команду с 51 или более акциями для этой станции
    cursor.execute('''
        SELECT c.command_id, c.name_command, SUM(us.amount) as total_shares
        FROM commands c
        JOIN users u ON c.command_id = u.command_id
        JOIN user_stocks us ON u.user_id = us.user_id
        WHERE us.station_id = ?
        GROUP BY c.command_id
        HAVING total_shares >= 51
    ''', (station_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {'command_id': result[0], 'name': result[1], 'shares': result[2]}
    return None



# Функция для получения ID команды по её имени
def get_command_id_by_name(command_name):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    cursor.execute('SELECT command_id FROM commands WHERE name_command = ?', (command_name,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


# Функция для перевода баланса команде
def admin_transfer_balance(command_id, amount, procient=0):
    try:
        conn = sqlite3.connect('game.db')
        cursor = conn.cursor()

        # Получаем текущий баланс команды
        cursor.execute('SELECT balance FROM commands WHERE command_id = ?', (command_id,))
        current_balance = cursor.fetchone()[0]

        # Рассчитываем новый баланс с учетом процента
        if procient > 0:
            bonus = amount * procient / 100
            new_balance = current_balance + amount + bonus
        else:
            new_balance = current_balance + amount

        # Обновляем баланс
        cursor.execute('UPDATE commands SET balance = ? WHERE command_id = ?',
                       (new_balance, command_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка при переводе баланса: {e}")
        if conn:
            conn.close()
        return False


@bot.message_handler(func=lambda message: message.text == 'Купить акции')
def transfer(message):  
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "АГАА, ПОПАЛСЯ ШКОЛЬНИК(ЦА), С KALI LINUX")
        main_menu(message.chat.id)
        return
    bot.send_message(message.chat.id, f'Вы выбрали: {message.text}')
    res = get_all_stationscode()
    message_text = 'Доступные акции:'
    for i in res:
        station_id = get_station_by_stationcode(i)
        action_amount = get_available_stocks(station_id)
        message_text += f'{i} : {action_amount} \n'
    bot.send_message(message.chat.id, message_text)

    bot.send_message(message.chat.id, 'Введите: Имя пользователя, станцию для покупки, количество акций(покупает пользователь) ')
    bot.register_next_step_handler(message, admin_action_buyng)
def admin_action_buyng(message):
    message_vals = message.text.split(",")
    if len(message_vals) != 3:
        bot.send_message(message.chat.id, f'Возможно вы ввели команду непраивльно. Пример "Sir_Sinion, Матфак, 10"', reply_markup=fei_menu())
        return
    
    user_id, command_id = get_user_by_username(message_vals[0])
    station_id = get_station_by_stationcode(message_vals[1].strip())
    amount = int(message_vals[2])
    res = buy_stocks(user_id, station_id, amount)

    if res:
        bot.send_message(message.chat.id, f"Акци куплены пользовавтелем", reply_markup=fei_menu())
    else:
        bot.send_message(message.chat.id, f'Ошибка при транзакции', reply_markup=fei_menu())

@bot.message_handler(func=lambda message: message.text == 'Продать акции')
def transfer(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "АГАА, ПОПАЛСЯ ШКОЛЬНИК(ЦА), С KALI LINUX")
        main_menu(message.chat.id)
        return
    res = get_all_stationscode()
    message_text = 'Доступные акции:'
    for i in res:
        station_id = get_station_by_stationcode(i)
        action_amount = get_available_stocks(station_id)
        message_text += f'{i} : {action_amount} \n'
    bot.send_message(message.chat.id, message_text)
    bot.send_message(message.chat.id, 'Введите: Имя пользователя, станцию для продажи, количество акций(продаёт пользователь) ')
    bot.register_next_step_handler(message, admin_action_selling)
def admin_action_selling(message):
    message_vals = message.text.split(",")
    if len(message_vals) != 3:
        bot.send_message(message.chat.id, f'Возможно вы ввели команду непраивльно. Пример "Sir_Sinion, Матфак, 10"', reply_markup=fei_menu())
        return
    
    user_id, command_id = get_user_by_username(message_vals[0])
    station_id = get_station_by_stationcode(message_vals[1].strip())
    amount = int(message_vals[2])
    
    res = sell_stocks(user_id, station_id, amount)

    if res:
        bot.send_message(message.chat.id, f"Акци проданы пользовавтелем", reply_markup=fei_menu())
    else:
        bot.send_message(message.chat.id, f'Ошибка при транзакции', reply_markup=fei_menu())

#Хендлер самого ИМПЕРАТОРА
@bot.message_handler(func=lambda message: message.text == 'Добавить команду')
def create_command_select(message):
    if message.chat.id not in MAIN_ADMINS:
        bot.send_message(message.chat.id, "АГАА, ПОПАЛСЯ ШКОЛЬНИК(ЦА), С KALI LINUX")
        main_menu(message.chat.id)
        return
    commands = get_all_commands()
    message_text = 'Хочу напомнить что уже существуют команды:\n'
    for command in commands:
        message_text += str(command) + "\n"
    bot.send_message(message.chat.id, message_text)
    bot.send_message(message.chat.id,"Введи имя новой команды:")
    bot.register_next_step_handler(message, create_command)
def create_command(message):
    
    add_command(message.text,1000)
    bot.send_message(message.chat.id, 'Команда добавлена', reply_markup=EMPEROR_menu())
    
@bot.message_handler(func=lambda message: message.text == 'Удалить команду')
def delete_command_select(message):
    if message.chat.id not in MAIN_ADMINS:
        bot.send_message(message.chat.id, "АГАА, ПОПАЛСЯ ШКОЛЬНИК(ЦА), С KALI LINUX")
        main_menu(message.chat.id)
        return
    commands = get_all_commands()
    message_text = 'Хочу напомнить что уже существуют команды:\n'
    for command in commands:
        message_text += str(command) + "\n"
    bot.send_message(message.chat.id, message_text)
    bot.send_message(message.chat.id, "Введите название команды, которую хотите удалить:")
    bot.register_next_step_handler(message, delete_command)
def delete_command(message):
    res = remove_command(message.text)
    if res:
        bot.send_message(message.chat.id, "Команда успешно удалена")
    else:
        bot.send_message(message.chat.id, "Возникли траблы")

@bot.message_handler(func=lambda message: message.text == 'Изменить акции')
def change_actions(message):
    stations = get_all_stationscode()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for station in stations:
        item = types.KeyboardButton(station)
        markup.add(item)
    markup.add('Главное меню')
    bot.send_message(message.chat.id,"Выберете станцию, для изменения акций", reply_markup=markup)
    bot.register_next_step_handler(message, change_actions_value)
def change_actions_value(message):
    if message.text not in get_all_stationscode():
        bot.send_message(message.chat.id,"Такой станции нет", reply_markup=EMPEROR_menu())
        return
    bot.send_message(message.chat.id,"Введите новую цену акций")
    bot.register_next_step_handler(message, change_actions_fin, station=message.text)
def change_actions_fin(message, station):
    station_id = get_station_by_stationcode(station)
    try:
        new_walut = int(message.text)
        update_stock_price(station_id, new_walut)
        bot.send_message(message.chat.id,"Успешно!", reply_markup=EMPEROR_menu())
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id,"Траблы, брат!", reply_markup=EMPEROR_menu())

@bot.message_handler(func=lambda message: message.text == 'Изменить акции%')
def change_actions(message):
    stations = get_all_stationscode()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for station in stations:
        item = types.KeyboardButton(station)
        markup.add(item)
    markup.add('Главное меню')
    bot.send_message(message.chat.id,"Выберете станцию, для изменения акций", reply_markup=markup)
    bot.register_next_step_handler(message, change_actions_procent)
def change_actions_procent(message):
    if message.text not in get_all_stationscode():
        bot.send_message(message.chat.id,"Такой станции нет", reply_markup=EMPEROR_menu())
        return
    bot.send_message(message.chat.id,"Введите процент изменения")
    bot.register_next_step_handler(message, change_actions_procent_fin, station=message.text)
def change_actions_procent_fin(message, station):
    station_id = get_station_by_stationcode(station)
    try:
        procent = int(message.text)/100
        old_price = int(get_station_cost(station)) 
        new_price = old_price + old_price*procent
        res = update_stock_price(station_id, int(new_price))
        if res:
            bot.send_message(message.chat.id,"Успешно!", reply_markup=EMPEROR_menu())
        else:
            raise ValueError
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id,"Траблы, брат!", reply_markup=EMPEROR_menu())

# @bot.message_handler(func=lambda message: message.text == 'Редактировать баланс')
# def tithing(message):


# Хендлер для выбора станции (для администраторов)
@bot.message_handler(func=lambda message: message.text in stations)
def admin_station(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "АГАА, ПОПАЛСЯ ШКОЛЬНИК(ЦА), С KALI LINUX")
        main_menu(message.chat.id)
        return
    selected_station = message.text
    bot.send_message(message.chat.id, f'Вы выбрали станцию: {selected_station}')
    if selected_station == 'Биржа':
        bot.send_message(message.chat.id, 'Теперь вы админ биржи?', reply_markup=fei_menu())
        return
    # Показываем кнопку "Переводы" после выбора станции
    bot.send_message(message.chat.id, 'Что бы вы хотели сделать?', reply_markup=admin_menu())

# Хендлер для кнопки "Команда" — возвращаем пользователя в меню действий
@bot.message_handler(func=lambda message: message.text == 'Команда')
def show_team_info(message):
    user_data = get_user_by_username(message.from_user.username)

    if not user_data:
        bot.send_message(message.chat.id, "Вы не зарегистрированы в системе.")
        return

    user_id, command_id = user_data

    if not command_id:
        bot.send_message(message.chat.id, "Вы не состоите в команде.")
        return

    command_info = get_command_info(command_id)
    formatted_info = format_command_info(command_info)

    bot.send_message(message.chat.id, formatted_info, reply_markup=user_action_menu())
# Хендлер для "Главного меню"
@bot.message_handler(func=lambda message: message.text == 'Главное меню')
def back_to_main_menu(message):
    if message.from_user.id in admins:
        # Для админа показываем выбор станций
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for station in stations:
            item = types.KeyboardButton(station)
            markup.add(item)
        markup.add('Главное меню')
        bot.send_message(message.chat.id, 'Выберите станцию:', reply_markup=markup)
    elif message.from_user.id in MAIN_ADMINS:
        bot.send_message(message.chat.id, 'Главное меню:', reply_markup=EMPEROR_menu())        
    else:
        # Для обычного пользователя показываем меню после выбора команды
        bot.send_message(message.chat.id, 'Что бы вы хотели сделать?', reply_markup=user_action_menu())


if __name__ == '__main__':
    bot.polling(none_stop=True)