import telebot
import sqlite3

token = '7690563368:AAGbrhslXKcCqvPgJ8QByW0Y2fAzO8unzUA'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
    conn = sqlite3.connect('game.db')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(50))')
    bot.send_message(message.chat.id, "Привет ✌️, это я Мойша_бот, скажи кто ты, участник или админ? ")
