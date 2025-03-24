import threading
import telebot
import time
from web_server import app
import index


def run_bot():
    print("Запуск Telegram бота...")
    try:
        from index import bot

        bot.infinity_polling()
        pass
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")


def run_web_server():
    print("Запуск веб-сервера...")
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == "__main__":
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()

    run_bot()

    # Если бот завершил работу, ждем завершения веб-сервера
    web_thread.join()
