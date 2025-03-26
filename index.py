import sqlite3
import telebot
from telebot import types

from config import TOKEN
from db import add_user, get_all_commands, get_all_stations, get_command_id_by_name, get_user_by_username, \
    update_user_command, get_command_info, format_command_info, get_balance, get_user_command_id, get_command_name_by_id, \
    transfer_balance, admin_transfer_balance, buy_stocks, get_station_by_stationcode, get_all_stationscode,\
    get_available_stocks, sell_stocks, get_user_stocks, transfer_stocks

commands = get_all_commands()
bot = telebot.TeleBot(TOKEN)
stations = get_all_stations()
# Список ID администраторов
me = 807802225
admins = [me]


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
    markup.add('Переводы','Купить акции(только ФЭИ)','Продать акции(только ФЭИ)', 'Главное меню')
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
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in admins:
        stations = get_all_stations()
        # Если пользователь админ, показываем список станций
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for station in stations:
            item = types.KeyboardButton(station)
            markup.add(item)
        markup.add('Главное меню')
        bot.send_message(message.chat.id, 'Выберите станцию:', reply_markup=markup)
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
    commands = get_all_commands()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for command in commands:
        item = types.KeyboardButton(command)
        markup.add(item)
    markup.add('Главное меню')
    bot.send_message(message.chat.id, 'Выберете команду для перевода валюты', reply_markup = markup)
    bot.register_next_step_handler(message, admin_money_transfer_value)
def admin_money_transfer_value(message):
    command = message.text
    if command not in commands: 
        bot.send_message(message.chat.id, 'К сожалению такой команды несуществует')
        main_menu(message.chat.id)
        return
    bot.send_message(message.chat.id, 'Введите сумму перевода и процент(если есть) через запятую')
    bot.register_next_step_handler(message, admin_money_transfer, command=command)
def admin_money_transfer(message, command):
    try:
        message_vals = message.text.split(",") 
        command_to = get_command_id_by_name(command)
        amout = int(message_vals[0])
        procient = 0
        if len(message_vals) == 2:
            procient = int(message_vals[1])
        transfer = admin_transfer_balance(command_to, amout, procient)
        if not transfer:
            bot.send_message(message.chat.id, f'Ошибка при переводе', reply_markup=admin_menu())
        else:
            bot.send_message(message.chat.id, f'Перевод выполнен!', reply_markup=admin_menu())
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, f'Упс, что-то пошло не так', reply_markup=admin_menu())

@bot.message_handler(func=lambda message: message.text == 'Купить акции(только ФЭИ)')
def transfer(message):
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
        bot.send_message(message.chat.id, f'Возможно вы ввели команду непраивльно. Пример "Sir_Sinion, Матфак, 10"', reply_markup=admin_menu())
        return
    
    user_id, command_id = get_user_by_username(message_vals[0])
    station_id = get_station_by_stationcode(message_vals[1].strip())
    amount = int(message_vals[2])
    res = buy_stocks(user_id, station_id, amount)

    if res:
        bot.send_message(message.chat.id, f"Акци куплены пользовавтелем", reply_markup=admin_menu())
    else:
        bot.send_message(message.chat.id, f'Ошибка при транзакции', reply_markup=admin_menu())

@bot.message_handler(func=lambda message: message.text == 'Продать акции(только ФЭИ)')
def transfer(message):
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
        bot.send_message(message.chat.id, f'Возможно вы ввели команду непраивльно. Пример "Sir_Sinion, Матфак, 10"', reply_markup=admin_menu())
        return
    
    user_id, command_id = get_user_by_username(message_vals[0])
    station_id = get_station_by_stationcode(message_vals[1].strip())
    amount = int(message_vals[2])
    
    res = sell_stocks(user_id, station_id, amount)

    if res:
        bot.send_message(message.chat.id, f"Акци проданы пользовавтелем", reply_markup=admin_menu())
    else:
        bot.send_message(message.chat.id, f'Ошибка при транзакции', reply_markup=admin_menu())

# Хендлер для выбора станции (для администраторов)
@bot.message_handler(func=lambda message: message.text in stations)
def admin_station(message):
    selected_station = message.text
    bot.send_message(message.chat.id, f'Вы выбрали станцию: {selected_station}')

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
    else:
        # Для обычного пользователя показываем меню после выбора команды
        bot.send_message(message.chat.id, 'Что бы вы хотели сделать?', reply_markup=user_action_menu())

if __name__ == '__main__':
    bot.polling(none_stop=True)