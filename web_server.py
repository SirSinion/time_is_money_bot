from flask import Flask, render_template_string
import sqlite3
from config import DATABASE

app = Flask(__name__)

@app.route('/')
def index():
    # Получаем данные из БД
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Чтобы получать данные в виде словарей
    cursor = conn.cursor()

    # Получаем список всех таблиц в БД
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Словарь для хранения данных всех таблиц
    all_tables_data = {}

    # Для каждой таблицы получаем все строки и заголовки
    for table in tables:
        table_name = table['name']
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        all_tables_data[table_name] = {
            'columns': columns,
            'rows': rows
        }

    conn.close()

    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>База данных Telegram бота</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            h1 {
                color: #333;
            }
            h2 {
                color: #666;
                margin-top: 30px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
                font-weight: bold;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f1f1f1;
            }
        </style>
    </head>
    <body>
        <h1>База данных Telegram бота</h1>

        {% for table_name, table_data in all_tables_data.items() %}
            <h2>Таблица: {{ table_name }}</h2>
            <table>
                <thead>
                    <tr>
                        {% for column in table_data.columns %}
                            <th>{{ column }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in table_data.rows %}
                        <tr>
                            {% for column in table_data.columns %}
                                <td>{{ row[column] }}</td>
                            {% endfor %}
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endfor %}
    </body>
    </html>
    '''

    return render_template_string(html_template, all_tables_data=all_tables_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
