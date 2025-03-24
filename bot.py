import telebot
from telebot import types
from config import TOKEN

bot = telebot.TeleBot(TOKEN, skip_pending=True)
me = 807802225
# Список ID администраторов
MAIN_ADMIN_ID = 111111  # Замените на реальный Telegram ID главного админа

# Список ID администраторов
admins = [333333333]  # Добавьте ID обычных админов

# Массив команд для пользователей (можно добавлять и удалять)
commands = ['Команда 1', 'Команда 2', 'Команда 3', 'Команда 4']

# Массив станций для админов
stations = ['Станция 1', 'Станция 2', 'Станция 3']

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

# Функция для создания меню главного администратора
def main_admin_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Добавить команду', 'Удалить команду', 'Главное меню')
    return markup

# Функция для меню выбора действия акций (перевод и т.д.)
def action_action_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Перевод', 'Главное меню')
    return markup

# Функция для меню выбора действия баланса (перевод и т.д.)
def balance_action_menu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Перевод', 'Главное меню')
    return markup

# Хендлер для команды /start
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == MAIN_ADMIN_ID:
        # Главное меню главного админа
        bot.send_message(message.chat.id, 'Добро пожаловать, главный администратор!', reply_markup=main_admin_menu())
    elif message.from_user.id in admins:
        # Если пользователь админ, показываем список станций
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for station in stations:
            item = types.KeyboardButton(station)
            markup.add(item)
        markup.add('Главное меню')
        bot.send_message(message.chat.id, 'Выберите станцию:', reply_markup=markup)
    else:
        # Если пользователь не админ, показываем список команд
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for command in commands:
            item = types.KeyboardButton(command)
            markup.add(item)
        markup.add('Главное меню')
        bot.send_message(message.chat.id, 'Выберите команду:', reply_markup=markup)

# Хендлер для выбора команды (для пользователей)
@bot.message_handler(func=lambda message: message.text in commands)
def user_command(message):
    bot.send_message(message.chat.id, f'Вы выбрали команду: {message.text}')
    bot.send_message(message.chat.id, 'Что бы вы хотели сделать?', reply_markup=user_action_menu())

# Хендлер для выбора "Команда" (возвращение в меню действий)
@bot.message_handler(func=lambda message: message.text == 'Команда')
def back_to_user_action_menu(message):
    bot.send_message(message.chat.id, 'Что бы вы хотели сделать?', reply_markup=user_action_menu())

# Хендлер для выбора действия внутри "Баланс" или "Акции"
@bot.message_handler(func=lambda message: message.text == 'Баланс')
def balance_or_promotions(message):
    bot.send_message(message.chat.id, f'Вы выбрали: {message.text}')
    bot.send_message(message.chat.id, f'Что бы вы хотели сделать с {message.text.lower()}?', reply_markup=balance_action_menu())

@bot.message_handler(func=lambda message: message.text == 'Акции')
def balance_or_promotions(message):
    bot.send_message(message.chat.id, f'Вы выбрали: {message.text}')
    bot.send_message(message.chat.id, f'Что бы вы хотели сделать с {message.text.lower()}?', reply_markup=action_action_menu())
    

# Хендлер для действия "Перевод"
@bot.message_handler(func=lambda message: message.text == 'Перевод')
def transfer(message):
    bot.send_message(message.chat.id, 'Введите команду, размер перевода и процент при бафах/дебафов (_Команду_ _Размер_ _процент(опционально)_)')
    bot.register_next_step_handler(message, money_transfer)

def money_transfer(message):
    bot.send_message(message.chat.id, f'Перевод выполнен!', reply_markup=user_action_menu())
    

# Хендлер для выбора станции (для администраторов)
@bot.message_handler(func=lambda message: message.text in stations)
def admin_station(message):
    bot.send_message(message.chat.id, f'Вы выбрали станцию: {message.text}')
    bot.send_message(message.chat.id, 'Что бы вы хотели сделать?', reply_markup=admin_menu())

# Хендлер для "Переводы" (для админов)
@bot.message_handler(func=lambda message: message.text == 'Переводы')
def admin_transfer(message):
    bot.send_message(message.chat.id, 'Перевод админом выполнен!', reply_markup=admin_menu())


# Хендлер для "Главного меню"
@bot.message_handler(func=lambda message: message.text == 'Главное меню')
def back_to_main_menu(message):
    if message.from_user.id == MAIN_ADMIN_ID:
        bot.send_message(message.chat.id, 'Вы в главном меню.', reply_markup=main_admin_menu())
    elif message.from_user.id in admins:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for station in stations:
            item = types.KeyboardButton(station)
            markup.add(item)
        markup.add('Главное меню')
        bot.send_message(message.chat.id, 'Выберите станцию:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Что бы вы хотели сделать?', reply_markup=user_action_menu())

# Хендлер для "Добавить команду" (только для главного админа)
@bot.message_handler(func=lambda message: message.text == 'Добавить команду')
def add_command(message):
    if message.from_user.id == MAIN_ADMIN_ID:
        bot.send_message(message.chat.id, 'Введите название новой команды:')
        bot.register_next_step_handler(message, save_new_command)
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа к этой функции!')

def save_new_command(message):
    new_command = message.text
    if new_command not in commands:
        commands.append(new_command)
        bot.send_message(message.chat.id, f'Команда "{new_command}" добавлена!', reply_markup=main_admin_menu())
    else:
        bot.send_message(message.chat.id, 'Такая команда уже существует.', reply_markup=main_admin_menu())

# Хендлер для "Удалить команду" (только для главного админа)
@bot.message_handler(func=lambda message: message.text == 'Удалить команду')
def remove_command(message):
    if message.from_user.id == MAIN_ADMIN_ID:
        if commands:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            for command in commands:
                markup.add(command)
            markup.add('Отмена')
            bot.send_message(message.chat.id, 'Выберите команду для удаления:', reply_markup=markup)
            bot.register_next_step_handler(message, delete_selected_command)
        else:
            bot.send_message(message.chat.id, 'Список команд пуст.', reply_markup=main_admin_menu())
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа к этой функции!')

def delete_selected_command(message):
    if message.text in commands:
        commands.remove(message.text)
        bot.send_message(message.chat.id, f'Команда "{message.text}" удалена.', reply_markup=main_admin_menu())
    elif message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Операция отменена.', reply_markup=main_admin_menu())
    else:
        bot.send_message(message.chat.id, 'Команда не найдена.', reply_markup=main_admin_menu())

if __name__ == '__main__':
    bot.polling(none_stop=True)