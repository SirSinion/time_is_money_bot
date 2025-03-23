import telebot
import sqlite3
token='7900245932:AAEHABitMTniyRHo_pAxvEjE_Phk-ZBh0Q8'
bot=telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start_message(message):
  conn = sqlite3.connect('main.db')
  cur = conn.cursor()

  cur.execute('CREATE TABLE IF NOT EXIST users(id int auto_incement primary key, name varchar(50),)')
  bot.send_message(message.chat.id,"Привет ✌️, это я Мойша_бот, скажи кто ты, участник или админ? ")


bot.infinity_poling()
