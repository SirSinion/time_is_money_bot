from flask import Flask, render_template, jsonify
import sqlite3
app = Flask(__name__)
DB_PATH = 'game.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Main page showing stock prices"""
    return render_template('index.html')


@app.route('/transactions')
def transactions():
    """Page showing transaction history"""
    return render_template('transactions.html')


@app.route('/team-capital')
def team_capital():
    """Page showing team capital chart"""
    return render_template('team_capital.html')


@app.route('/api/stocks')
def get_stocks():
    """API endpoint to get stock data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all stations (stocks)
    cursor.execute('SELECT station_id, name, code, description, price FROM stations ORDER BY name')
    stations = cursor.fetchall()

    # Convert to list of dictionaries for JSON response
    stocks = []
    for station in stations:
        stocks.append({
            'id': station['station_id'],
            'name': station['name'],
            'code': station['code'],
            'description': station['description'],
            'price': station['price']
        })

    conn.close()
    return jsonify(stocks)

@app.route('/api/transactions')
def get_transactions():
    """API endpoint to get transaction history"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get transaction history by joining user_stocks, users, and stations tables
    cursor.execute('''
        SELECT 
            us.id, 
            u.username, 
            c.name_command as team_name,
            s.name as stock_name, 
            s.code as stock_code,
            us.amount, 
            us.purchase_price,
            (us.amount * us.purchase_price) as total_price
        FROM user_stocks us
        JOIN users u ON us.user_id = u.user_id
        JOIN stations s ON us.station_id = s.station_id
        JOIN commands c ON u.command_id = c.command_id
        ORDER BY us.id DESC
        LIMIT 100
    ''')

    transactions = cursor.fetchall()

    # Convert to list of dictionaries for JSON response
    result = []
    for transaction in transactions:
        result.append({
            'id': transaction['id'],
            'username': transaction['username'],
            'team_name': transaction['team_name'],
            'stock_name': transaction['stock_name'],
            'stock_code': transaction['stock_code'],
            'amount': transaction['amount'],
            'purchase_price': transaction['purchase_price'],
            'total_price': transaction['total_price']
        })

    conn.close()
    return jsonify(result)


@app.route('/api/team-capital')
def get_team_capital():
    """API endpoint to get team capital data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get team capital data
    cursor.execute('''
        SELECT 
            c.command_id,
            c.name_command,
            c.balance
        FROM commands c
        ORDER BY c.balance DESC
    ''')

    teams = cursor.fetchall()

    # For each team, calculate total stock value
    result = []
    for team in teams:
        command_id = team['command_id']

        # Get all stocks owned by team members
        cursor.execute('''
            SELECT 
                SUM(us.amount * s.price) as stock_value
            FROM user_stocks us
            JOIN users u ON us.user_id = u.user_id
            JOIN stations s ON us.station_id = s.station_id
            WHERE u.command_id = ?
        ''', (command_id,))

        stock_value = cursor.fetchone()['stock_value'] or 0
        total_capital = team['balance'] + stock_value

        result.append({
            'id': team['command_id'],
            'name': team['name_command'],
            'balance': team['balance'],
            'stock_value': stock_value,
            'total_capital': total_capital
        })

    # Sort by total capital
    result.sort(key=lambda x: x['total_capital'], reverse=True)

    conn.close()
    return jsonify(result)