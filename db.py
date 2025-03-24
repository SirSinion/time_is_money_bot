import sqlite3
from typing import Tuple, Optional, List


def create_database():
    # Удаляем существующую базу данных, если она есть
    # (можно закомментировать, если вы не хотите удалять данные при каждом запуске)
    import os
    if os.path.exists('game.db'):
        os.remove('game.db')

    # Создаем новое подключение
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    # 1. Таблица команды
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS commands (
        command_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_command TEXT,
        balance INTEGER DEFAULT 0
    )
    ''')

    # 2. Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        command_id INTEGER,
        FOREIGN KEY (command_id) REFERENCES commands(command_id)
    )
    ''')

    # 3. Таблица станций
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stations (
        station_id INTEGER PRIMARY KEY,
        name TEXT,
        code TEXT,
        description TEXT,
        price INTEGER DEFAULT 100
    )
    ''')

    # 4. Таблица акций пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        station_id INTEGER,
        amount INTEGER DEFAULT 0,
        purchase_price INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (station_id) REFERENCES stations(station_id)
    )
    ''')

    # Заполнение таблицы станций начальными данными
    stations = [
        (1, "Биржа", "ФЭИ", "Здесь можно торговать акциями и получать прибыль", 100),
        (2, "Казино", "МФ", "Игры с расчетом шансов и вероятностей", 100),
        (3, "Интеллектуальная станция", "СОФУМ", "Вопросы по истории, философии, литературе", 100),
        (4, "Черный рынок", "ИГиП", "Юридические сделки и 'серые схемы'", 100),
        (5, "Физическая станция", "СОК", "Работа, физические задания", 100),
        (6, "Аукцион с бафами", "ШЭН", "Временные бонусы для получения выгоды", 100),
        (7, "Стартап-инкубатор", "SAS", "Разработка идей, решение микрокейсов", 100),
        (8, "Музыкальная станция", "ИПиП", "Музыкальные задания", 100)
    ]

    cursor.executemany("INSERT OR IGNORE INTO stations VALUES (?, ?, ?, ?, ?)", stations)

    # Добавим тестовую команду
    cursor.execute("INSERT INTO commands (name_command, balance) VALUES (?, ?)",
                   ("Тестовая команда", 1000))

    conn.commit()
    conn.close()
    print("База данных успешно создана!")

def connect_db() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Создает подключение к базе данных и возвращает соединение и курсор"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    return conn, cursor


def close_db(conn: sqlite3.Connection, commit: bool = True) -> None:
    """Закрывает соединение с базой данных"""
    if commit:
        conn.commit()
    conn.close()

#Добавление комманды
def add_command(name_command: str, initial_balance: int = 0) -> int:
    """
    Добавляет новую команду в базу данных.

    Args:
        name_command: Название команды
        initial_balance: Начальный баланс команды (по умолчанию 0)

    Returns:
        ID созданной команды
    """
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    try:
        # Проверяем, существует ли уже команда с таким названием
        cursor.execute("SELECT command_id FROM commands WHERE name_command = ?", (name_command,))
        existing_command = cursor.fetchone()

        if existing_command:
            raise ValueError(f"Команда с названием '{name_command}' уже существует")

        # Добавляем новую команду
        cursor.execute(
            "INSERT INTO commands (name_command, balance) VALUES (?, ?)",
            (name_command, initial_balance)
        )

        # Получаем ID созданной команды
        command_id = cursor.lastrowid
        conn.commit()
        return command_id

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()


# Функции для работы с балансом
def add_user(username: str, command_id: Optional[int] = None) -> int:
    """
    Добавляет нового пользователя в базу данных.

    Args:
        username: Имя пользователя
        command_id: ID команды, к которой будет привязан пользователь

    Returns:
        ID созданного пользователя
    """
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    try:
        # Если command_id не указан, пользователь добавляется без команды
        if command_id is None:
            cursor.execute(
                "INSERT INTO users (username) VALUES (?)",
                (username,)
            )
        else:
            # Проверяем, существует ли команда с указанным ID
            cursor.execute("SELECT command_id FROM commands WHERE command_id = ?", (command_id,))
            if not cursor.fetchone():
                raise ValueError(f"Команда с ID {command_id} не существует")

            cursor.execute(
                "INSERT INTO users (username, command_id) VALUES (?, ?)",
                (username, command_id)
            )

        # Получаем ID созданного пользователя
        user_id = cursor.lastrowid
        conn.commit()
        return user_id

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()


def add_user_to_command(user_id: int, command_id: int) -> bool:
    """
    Добавляет существующего пользователя в команду.

    Args:
        user_id: ID пользователя
        command_id: ID команды

    Returns:
        True, если пользователь успешно добавлен в команду, иначе False
    """
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    try:
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            print(f"Пользователь с ID {user_id} не существует")
            return False

        # Проверяем, существует ли команда
        cursor.execute("SELECT command_id FROM commands WHERE command_id = ?", (command_id,))
        if not cursor.fetchone():
            print(f"Команда с ID {command_id} не существует")
            return False

        # Обновляем команду пользователя
        cursor.execute(
            "UPDATE users SET command_id = ? WHERE user_id = ?",
            (command_id, user_id)
        )

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(f"Ошибка при добавлении пользователя в команду: {e}")
        return False

    finally:
        conn.close()


def get_user_info(user_id: int) -> Optional[Tuple]:
    """
    Получает информацию о пользователе по его ID.

    Args:
        user_id: ID пользователя

    Returns:
        Кортеж с информацией о пользователе или None, если пользователь не найден
    """
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT u.user_id, u.username, u.command_id, c.name_command 
            FROM users u
            LEFT JOIN commands c ON u.command_id = c.command_id
            WHERE u.user_id = ?
        """, (user_id,))

        user_info = cursor.fetchone()
        return user_info

    finally:
        conn.close()


def add_balance(command_id: int, amount: int) -> bool:
    """
    Добавляет указанную сумму к балансу команды

    Args:
        command_id: ID команды
        amount: Сумма для добавления (может быть отрицательной для снятия)

    Returns:
        True если операция успешна, False в противном случае
    """
    conn, cursor = connect_db()

    try:
        # Проверяем существование команды
        cursor.execute("SELECT balance FROM commands WHERE command_id = ?", (command_id,))
        result = cursor.fetchone()

        if not result:
            print(f"Команда с ID {command_id} не найдена")
            close_db(conn, commit=False)
            return False

        current_balance = result[0]
        new_balance = current_balance + amount

        # Не позволяем балансу стать отрицательным
        if new_balance < 0:
            print(f"Недостаточно средств. Текущий баланс: {current_balance}")
            close_db(conn, commit=False)
            return False

        # Обновляем баланс
        cursor.execute(
            "UPDATE commands SET balance = ? WHERE command_id = ?",
            (new_balance, command_id)
        )

        close_db(conn)
        return True

    except Exception as e:
        print(f"Ошибка при обновлении баланса: {e}")
        close_db(conn, commit=False)
        return False


def get_balance(command_id: int) -> Optional[int]:
    """
    Получает текущий баланс команды

    Args:
        command_id: ID команды

    Returns:
        Текущий баланс или None, если команда не найдена
    """
    conn, cursor = connect_db()

    try:
        cursor.execute("SELECT balance FROM commands WHERE command_id = ?", (command_id,))
        result = cursor.fetchone()

        close_db(conn, commit=False)
        return result[0] if result else None

    except Exception as e:
        print(f"Ошибка при получении баланса: {e}")
        close_db(conn, commit=False)
        return None


# Функции для работы с акциями

def get_available_stocks(station_id: int) -> int:
    """
    Получает количество доступных акций для станции

    Args:
        station_id: ID станции

    Returns:
        Количество доступных акций
    """
    conn, cursor = connect_db()

    try:
        # Получаем общее количество купленных акций этой станции
        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM user_stocks WHERE station_id = ?",
            (station_id,)
        )
        result = cursor.fetchone()

        # Всего 100 акций для каждой станции
        total_stocks = 100
        bought_stocks = result[0] if result else 0
        available_stocks = total_stocks - bought_stocks

        close_db(conn, commit=False)
        return available_stocks

    except Exception as e:
        print(f"Ошибка при получении доступных акций: {e}")
        close_db(conn, commit=False)
        return 0


def buy_stocks(user_id: int, station_id: int, amount: int) -> bool:
    """
    Покупка акций станции пользователем

    Args:
        user_id: ID пользователя
        station_id: ID станции
        amount: Количество акций для покупки

    Returns:
        True если операция успешна, False в противном случае
    """
    conn, cursor = connect_db()

    try:
        # Проверяем существование пользователя и получаем его команду
        cursor.execute("SELECT command_id FROM users WHERE user_id = ?", (user_id,))
        user_result = cursor.fetchone()

        if not user_result:
            print(f"Пользователь с ID {user_id} не найден")
            close_db(conn, commit=False)
            return False

        command_id = user_result[0]

        # Проверяем существование станции и получаем цену акций
        cursor.execute("SELECT price FROM stations WHERE station_id = ?", (station_id,))
        station_result = cursor.fetchone()

        if not station_result:
            print(f"Станция с ID {station_id} не найдена")
            close_db(conn, commit=False)
            return False

        stock_price = station_result[0]

        # Проверяем доступность акций
        available_stocks = get_available_stocks(station_id)
        if amount > available_stocks:
            print(f"Недостаточно доступных акций. Доступно: {available_stocks}")
            close_db(conn, commit=False)
            return False

        # Проверяем баланс команды
        total_cost = stock_price * amount
        current_balance = get_balance(command_id)

        if current_balance < total_cost:
            print(f"Недостаточно средств. Требуется: {total_cost}, баланс: {current_balance}")
            close_db(conn, commit=False)
            return False

        # Все проверки пройдены, выполняем транзакцию
        # 1. Снимаем деньги с баланса команды
        cursor.execute(
            "UPDATE commands SET balance = balance - ? WHERE command_id = ?",
            (total_cost, command_id)
        )

        # 2. Проверяем, есть ли у пользователя уже акции этой станции
        cursor.execute(
            "SELECT id, amount, purchase_price FROM user_stocks WHERE user_id = ? AND station_id = ?",
            (user_id, station_id)
        )
        existing_stock = cursor.fetchone()

        if existing_stock:
            # Обновляем существующую запись
            stock_id, existing_amount, existing_price = existing_stock

            # Рассчитываем новую среднюю цену покупки
            new_amount = existing_amount + amount
            new_avg_price = ((existing_amount * existing_price) + (amount * stock_price)) // new_amount

            cursor.execute(
                "UPDATE user_stocks SET amount = ?, purchase_price = ? WHERE id = ?",
                (new_amount, new_avg_price, stock_id)
            )
        else:
            # Создаем новую запись
            cursor.execute(
                "INSERT INTO user_stocks (user_id, station_id, amount, purchase_price) VALUES (?, ?, ?, ?)",
                (user_id, station_id, amount, stock_price)
            )

        close_db(conn)
        return True

    except Exception as e:
        print(f"Ошибка при покупке акций: {e}")
        close_db(conn, commit=False)
        return False


def sell_stocks(user_id: int, station_id: int, amount: int) -> bool:
    """
    Продажа акций станции пользователем

    Args:
        user_id: ID пользователя
        station_id: ID станции
        amount: Количество акций для продажи

    Returns:
        True если операция успешна, False в противном случае
    """
    conn, cursor = connect_db()

    try:
        # Проверяем существование пользователя и получаем его команду
        cursor.execute("SELECT command_id FROM users WHERE user_id = ?", (user_id,))
        user_result = cursor.fetchone()

        if not user_result:
            print(f"Пользователь с ID {user_id} не найден")
            close_db(conn, commit=False)
            return False

        command_id = user_result[0]

        # Проверяем существование станции и получаем текущую цену акций
        cursor.execute("SELECT price FROM stations WHERE station_id = ?", (station_id,))
        station_result = cursor.fetchone()

        if not station_result:
            print(f"Станция с ID {station_id} не найдена")
            close_db(conn, commit=False)
            return False

        current_price = station_result[0]

        # Проверяем, есть ли у пользователя акции этой станции
        cursor.execute(
            "SELECT id, amount FROM user_stocks WHERE user_id = ? AND station_id = ?",
            (user_id, station_id)
        )
        existing_stock = cursor.fetchone()

        if not existing_stock or existing_stock[1] < amount:
            print(f"У пользователя недостаточно акций. Доступно: {existing_stock[1] if existing_stock else 0}")
            close_db(conn, commit=False)
            return False

        stock_id, existing_amount = existing_stock

        # Рассчитываем сумму к получению
        total_income = current_price * amount

        # Выполняем транзакцию
        # 1. Добавляем деньги на баланс команды
        cursor.execute(
            "UPDATE commands SET balance = balance + ? WHERE command_id = ?",
            (total_income, command_id)
        )

        # 2. Обновляем количество акций пользователя
        new_amount = existing_amount - amount

        if new_amount == 0:
            # Если акций не осталось, удаляем запись
            cursor.execute("DELETE FROM user_stocks WHERE id = ?", (stock_id,))
        else:
            # Обновляем количество акций
            cursor.execute(
                "UPDATE user_stocks SET amount = ? WHERE id = ?",
                (new_amount, stock_id)
            )

        close_db(conn)
        return True

    except Exception as e:
        print(f"Ошибка при продаже акций: {e}")
        close_db(conn, commit=False)
        return False


def transfer_stocks(from_user_id: int, to_user_id: int, station_id: int, amount: int) -> bool:
    """
    Передача акций от одного пользователя другому

    Args:
        from_user_id: ID пользователя, который передает акции
        to_user_id: ID пользователя, который получает акции
        station_id: ID станции
        amount: Количество акций для передачи

    Returns:
        True если операция успешна, False в противном случае
    """
    conn, cursor = connect_db()

    try:
        # Проверяем существование пользователей
        cursor.execute("SELECT user_id FROM users WHERE user_id IN (?, ?)", (from_user_id, to_user_id))
        users = cursor.fetchall()

        if len(users) != 2:
            print("Один или оба пользователя не найдены")
            close_db(conn, commit=False)
            return False

        # Проверяем существование станции
        cursor.execute("SELECT station_id FROM stations WHERE station_id = ?", (station_id,))
        if not cursor.fetchone():
            print(f"Станция с ID {station_id} не найдена")
            close_db(conn, commit=False)
            return False

        # Проверяем, есть ли у отправителя достаточно акций
        cursor.execute(
            "SELECT id, amount, purchase_price FROM user_stocks WHERE user_id = ? AND station_id = ?",
            (from_user_id, station_id)
        )
        sender_stock = cursor.fetchone()

        if not sender_stock or sender_stock[1] < amount:
            print(f"У отправителя недостаточно акций. Доступно: {sender_stock[1] if sender_stock else 0}")
            close_db(conn, commit=False)
            return False

        sender_stock_id, sender_amount, purchase_price = sender_stock

        # Выполняем передачу акций
        # 1. Уменьшаем количество акций у отправителя
        new_sender_amount = sender_amount - amount

        if new_sender_amount == 0:
            # Если акций не осталось, удаляем запись
            cursor.execute("DELETE FROM user_stocks WHERE id = ?", (sender_stock_id,))
        else:
            # Обновляем количество акций
            cursor.execute(
                "UPDATE user_stocks SET amount = ? WHERE id = ?",
                (new_sender_amount, sender_stock_id)
            )

        # 2. Проверяем, есть ли у получателя акции этой станции
        cursor.execute(
            "SELECT id, amount, purchase_price FROM user_stocks WHERE user_id = ? AND station_id = ?",
            (to_user_id, station_id)
        )
        receiver_stock = cursor.fetchone()

        if receiver_stock:
            # Обновляем существующую запись
            receiver_stock_id, receiver_amount, receiver_price = receiver_stock

            # Рассчитываем новую среднюю цену покупки
            new_receiver_amount = receiver_amount + amount
            new_avg_price = ((receiver_amount * receiver_price) + (amount * purchase_price)) // new_receiver_amount

            cursor.execute(
                "UPDATE user_stocks SET amount = ?, purchase_price = ? WHERE id = ?",
                (new_receiver_amount, new_avg_price, receiver_stock_id)
            )
        else:
            # Создаем новую запись
            cursor.execute(
                "INSERT INTO user_stocks (user_id, station_id, amount, purchase_price) VALUES (?, ?, ?, ?)",
                (to_user_id, station_id, amount, purchase_price)
            )

        close_db(conn)
        return True

    except Exception as e:
        print(f"Ошибка при передаче акций: {e}")
        close_db(conn, commit=False)
        return False


def get_user_stocks(user_id: int) -> List[dict]:
    """
    Получает список всех акций пользователя

    Args:
        user_id: ID пользователя

    Returns:
        Список словарей с информацией об акциях пользователя
    """
    conn, cursor = connect_db()

    try:
        # Проверяем существование пользователя
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            print(f"Пользователь с ID {user_id} не найден")
            close_db(conn, commit=False)
            return []

        # Получаем все акции пользователя с информацией о станциях
        cursor.execute("""
            SELECT 
                us.station_id, 
                s.name, 
                s.code, 
                us.amount, 
                us.purchase_price, 
                s.price as current_price
            FROM 
                user_stocks us
            JOIN 
                stations s ON us.station_id = s.station_id
            WHERE 
                us.user_id = ?
        """, (user_id,))

        stocks = []
        for row in cursor.fetchall():
            station_id, name, code, amount, purchase_price, current_price = row

            # Рассчитываем прибыль/убыток
            profit_loss = (current_price - purchase_price) * amount
            profit_percent = ((current_price / purchase_price) - 1) * 100 if purchase_price > 0 else 0

            stocks.append({
                'station_id': station_id,
                'name': name,
                'code': code,
                'amount': amount,
                'purchase_price': purchase_price,
                'current_price': current_price,
                'total_value': current_price * amount,
                'profit_loss': profit_loss,
                'profit_percent': profit_percent
            })

        close_db(conn, commit=False)
        return stocks

    except Exception as e:
        print(f"Ошибка при получении акций пользователя: {e}")
        close_db(conn, commit=False)
        return []


def get_station_stocks_distribution(station_id: int) -> List[dict]:
    """
    Получает распределение акций станции между пользователями

    Args:
        station_id: ID станции

    Returns:
        Список словарей с информацией о владельцах акций
    """
    conn, cursor = connect_db()

    try:
        # Проверяем существование станции
        cursor.execute("SELECT station_id, name FROM stations WHERE station_id = ?", (station_id,))
        station = cursor.fetchone()

        if not station:
            print(f"Станция с ID {station_id} не найдена")
            close_db(conn, commit=False)
            return []

        station_name = station[1]

        # Получаем распределение акций между пользователями
        cursor.execute("""
            SELECT 
                u.user_id, 
                u.username, 
                c.name_command, 
                us.amount, 
                us.purchase_price
            FROM 
                user_stocks us
            JOIN 
                users u ON us.user_id = u.user_id
            JOIN 
                commands c ON u.command_id = c.command_id
            WHERE 
                us.station_id = ?
            ORDER BY 
                us.amount DESC
        """, (station_id,))

        distribution = []
        total_distributed = 0

        for row in cursor.fetchall():
            user_id, username, command_name, amount, purchase_price = row
            total_distributed += amount

            distribution.append({
                'user_id': user_id,
                'username': username,
                'command_name': command_name,
                'amount': amount,
                'percentage': (amount / 100) * 100,  # Всего 100 акций
                'purchase_price': purchase_price
            })

        # Добавляем информацию о нераспределенных акциях
        free_stocks = 100 - total_distributed
        if free_stocks > 0:
            distribution.append({
                'user_id': None,
                'username': 'Свободные акции',
                'command_name': None,
                'amount': free_stocks,
                'percentage': free_stocks,
                'purchase_price': None
            })

        close_db(conn, commit=False)
        return {
            'station_name': station_name,
            'distribution': distribution,
            'total_distributed': total_distributed,
            'free_stocks': free_stocks
        }

    except Exception as e:
        print(f"Ошибка при получении распределения акций: {e}")
        close_db(conn, commit=False)
        return []


def update_stock_price(station_id: int, new_price: int) -> bool:
    """
    Обновляет цену акций станции

    Args:
        station_id: ID станции
        new_price: Новая цена акций

    Returns:
        True если операция успешна, False в противном случае
    """
    conn, cursor = connect_db()

    try:
        # Проверяем существование станции
        cursor.execute("SELECT station_id FROM stations WHERE station_id = ?", (station_id,))
        if not cursor.fetchone():
            print(f"Станция с ID {station_id} не найдена")
            close_db(conn, commit=False)
            return False

        # Не позволяем устанавливать отрицательную цену
        if new_price <= 0:
            print("Цена акций должна быть положительной")
            close_db(conn, commit=False)
            return False

        # Обновляем цену акций
        cursor.execute(
            "UPDATE stations SET price = ? WHERE station_id = ?",
            (new_price, station_id)
        )

        close_db(conn)
        return True

    except Exception as e:
        print(f"Ошибка при обновлении цены акций: {e}")
        close_db(conn, commit=False)
        return False


def transfer_balance(from_command_id: int, to_command_id: int, amount: int) -> bool:
    """
    Переводит деньги с баланса одной команды на баланс другой

    Args:
        from_command_id: ID команды-отправителя
        to_command_id: ID команды-получателя
        amount: Сумма перевода

    Returns:
        True если операция успешна, False в противном случае
    """
    conn, cursor = connect_db()

    try:
        # Проверяем существование команд
        cursor.execute("SELECT command_id, balance FROM commands WHERE command_id IN (?, ?)",
                       (from_command_id, to_command_id))
        commands = cursor.fetchall()

        if len(commands) != 2:
            print("Одна или обе команды не найдены")
            close_db(conn, commit=False)
            return False

        # Определяем, какая команда отправитель, а какая получатель
        sender_balance = None
        for cmd in commands:
            if cmd[0] == from_command_id:
                sender_balance = cmd[1]

        if sender_balance is None:
            print(f"Команда-отправитель с ID {from_command_id} не найдена")
            close_db(conn, commit=False)
            return False

        # Проверяем достаточно ли средств у отправителя
        if sender_balance < amount:
            print(f"Недостаточно средств у команды-отправителя. Баланс: {sender_balance}, требуется: {amount}")
            close_db(conn, commit=False)
            return False

        # Выполняем перевод
        cursor.execute(
            "UPDATE commands SET balance = balance - ? WHERE command_id = ?",
            (amount, from_command_id)
        )

        cursor.execute(
            "UPDATE commands SET balance = balance + ? WHERE command_id = ?",
            (amount, to_command_id)
        )

        close_db(conn)
        return True

    except Exception as e:
        print(f"Ошибка при переводе средств: {e}")
        close_db(conn, commit=False)
        return False


def get_stock_market_summary() -> dict:
    """
    Получает сводку по рынку акций

    Returns:
        Словарь с информацией о всех станциях и распределении их акций
    """
    conn, cursor = connect_db()

    try:
        # Получаем информацию о всех станциях
        cursor.execute("SELECT station_id, name, code, price FROM stations")
        stations_data = cursor.fetchall()

        market_summary = []

        for station in stations_data:
            station_id, name, code, price = station

            # Получаем распределение акций для станции
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(amount), 0) as total_owned,
                    COUNT(DISTINCT user_id) as owners_count
                FROM 
                    user_stocks
                WHERE 
                    station_id = ?
            """, (station_id,))

            ownership_data = cursor.fetchone()
            total_owned = ownership_data[0]
            owners_count = ownership_data[1]
            free_stocks = 100 - total_owned

            market_summary.append({
                'station_id': station_id,
                'name': name,
                'code': code,
                'price': price,
                'total_owned': total_owned,
                'free_stocks': free_stocks,
                'owners_count': owners_count
            })

        close_db(conn, commit=False)
        return {'market_summary': market_summary}

    except Exception as e:
        print(f"Ошибка при получении сводки по рынку: {e}")
        close_db(conn, commit=False)
        return {'market_summary': []}


# Пример использования функций:
if __name__ == "__main__":
    # Создаем базу данных
    create_database()

    # Добавляем пользователя
    conn, cursor = connect_db()
    cursor.execute("INSERT INTO users (username, command_id) VALUES (?, ?)", ("Игрок1", 1))
    user_id = cursor.lastrowid
    close_db(conn)

    # Добавляем баланс команде
    add_balance(1, 5000)
    print(f"Баланс команды: {get_balance(1)}")

    # Покупаем акции
    buy_stocks(user_id, 1, 10)
    print(f"Доступно акций станции 1: {get_available_stocks(1)}")

    # Получаем акции пользователя
    user_stocks = get_user_stocks(user_id)
    print(f"Акции пользователя: {user_stocks}")

    # Обновляем цену акций
    update_stock_price(1, 150)

    # Получаем сводку по рынку
    market_summary = get_stock_market_summary()
    print(f"Сводка по рынку: {market_summary}")
