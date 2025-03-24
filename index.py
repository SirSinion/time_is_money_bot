import sqlite3
import telebot
from telebot import types
from config import TOKEN
from db import add_user, get_all_commands, get_all_stations, get_command_id_by_name, get_user_by_username, \
    update_user_command, get_command_info, format_command_info

commands = get_all_commands()
bot = telebot.TeleBot(TOKEN)
stations = get_all_stations()
# Список ID администраторов
admins = [123456789, 987654321]


# Функция для создания меню пользователя
def user_action_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Команда', 'Баланс', 'Акции')
    return markup


# Функция для создания меню администратора
def admin_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Переводы', 'Главное меню')
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


# Хендлер для команды /start
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in admins:
        # Если пользователь админ, показываем список станций
        stations = get_all_stations()
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

def user_action_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Команда', 'Баланс', 'Акции')
    return markup

# Функция для создания меню администратора
def admin_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Переводы', 'Главное меню')
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




# Хендлер для выбора действия внутри "Баланс" или "Акции"
@bot.message_handler(func=lambda message: message.text in ['Баланс', 'Акции'])
def balance_or_promotions(message):
    selected_action = message.text
    bot.send_message(message.chat.id, f'Вы выбрали: {selected_action}')

    # Добавляем кнопку "Перевод" внутри разделов "Баланс" и "Акции"
    bot.send_message(message.chat.id, f'Что бы вы хотели сделать с {selected_action.lower()}?', reply_markup=action_menu())



#TODO:
# Хендлер для действия "Перевод" (для пользователей)

# Хендлер для действия "Перевод"
@bot.message_handler(func=lambda message: message.text == 'Перевод')
def transfer(message):
    bot.send_message(message.chat.id,
                     'Введите команду, размер перевода и процент при бафах/дебафов (_Команду_ _Размер_ _процент(опционально)_)')
    bot.register_next_step_handler(message, money_transfer)

def money_transfer(message):
    bot.send_message(message.chat.id, f'Перевод выполнен!', reply_markup=user_action_menu())


# Хендлер для действия "Переводы" (для администраторов)
@bot.message_handler(func=lambda message: message.text == 'Переводы')
def admin_transfer(message):
    bot.send_message(message.chat.id, 'Перевод админом выполнен!')

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