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
def start_message(message):
    conn = sqlite3.connect('main.db')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(50))')
    bot.send_message(message.chat.id, "Привет ✌️, это я Мойша_бот, скажи кто ты, участник или админ? ")
