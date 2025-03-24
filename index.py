import telebot
from telebot import types
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

# Список ID администраторов
admins = [123456789, 987654321]

# Массив команд для пользователей
commands = ['Команда 1', 'Команда 2', 'Команда 3', 'Команда 4']

# Массив станций для админов
stations = ['Станция 1', 'Станция 2', 'Станция 3']

# Список ID администраторов
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

# Хендлер для команды /start
@bot.message_handler(commands=['start'])
<<<<<<< HEAD
def start(message):
    if message.from_user.id in admins:
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
=======
def start_message(message):
    conn = sqlite3.connect('game.db')
    cur = conn.cursor()
>>>>>>> a2ef2d63426dafa5cbfde0eace79e7a49844fc35

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

# Хендлер для действия "Перевод" (для пользователей)
@bot.message_handler(func=lambda message: message.text == 'Перевод')
def transfer(message):
    bot.send_message(message.chat.id, 'Перевод выполнен!')

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
def back_to_user_action_menu(message):
    bot.send_message(message.chat.id, 'Что бы вы хотели сделать?', reply_markup=user_action_menu())

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