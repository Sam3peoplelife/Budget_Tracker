from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import csv
from io import TextIOWrapper
from datetime import datetime

app = Flask(__name__)

# Ініціалізація бази даних
def init_db():
    with sqlite3.connect('transactions.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                title TEXT,
                amount REAL,
                category TEXT
            )
        ''')
        conn.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    # Отримання унікальних категорій для фільтру
    with sqlite3.connect('transactions.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM transactions')
        categories = [row[0] for row in cursor.fetchall()]

    # Параметри фільтрації
    category_filter = request.form.get('category', '')
    date_filter = request.form.get('date', '')
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')

    # Побудова SQL-запиту з фільтрами
    query = 'SELECT * FROM transactions WHERE 1=1'
    params = []

    if category_filter:
        query += ' AND category = ?'
        params.append(category_filter)
    if date_filter:
        query += ' AND date = ?'
        params.append(date_filter)
    if start_date and end_date:
        query += ' AND date BETWEEN ? AND ?'
        params.extend([start_date, end_date])

    # Виконання запиту
    with sqlite3.connect('transactions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        transactions = cursor.fetchall()

    return render_template('index.html', transactions=transactions, categories=categories,
                           category_filter=category_filter, date_filter=date_filter,
                           start_date=start_date, end_date=end_date)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.csv'):
        csv_file = TextIOWrapper(file, encoding='utf-8')
        csv_reader = csv.DictReader(csv_file)
        
        required_columns = {'date', 'title', 'amount', 'category'}
        if not required_columns.issubset(csv_reader.fieldnames):
            return "CSV file must contain 'date', 'title', 'amount', and 'category' columns", 400
        
        with sqlite3.connect('transactions.db') as conn:
            cursor = conn.cursor()
            for row in csv_reader:
                try:
                    datetime.strptime(row['date'], '%Y-%m-%d')
                    amount = float(row['amount'])
                    cursor.execute('''
                        INSERT INTO transactions (date, title, amount, category)
                        VALUES (?, ?, ?, ?)
                    ''', (row['date'], row['title'], amount, row['category']))
                except ValueError:
                    continue
            conn.commit()
        
        return redirect(url_for('index'))
    
    return "Invalid file format. Please upload a CSV file.", 400

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    with sqlite3.connect('transactions.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM transactions')
        categories = [row[0] for row in cursor.fetchall()]

    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')

    query = 'SELECT * FROM transactions'
    params = []
    if start_date and end_date:
        query += ' WHERE date BETWEEN ? AND ?'
        params.extend([start_date, end_date])
    query += ' ORDER BY date DESC'

    with sqlite3.connect('transactions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        transactions = cursor.fetchall()

    return render_template('manage.html', transactions=transactions, categories=categories,
                           start_date=start_date, end_date=end_date)

@app.route('/add', methods=['POST'])
def add_transaction():
    date = request.form.get('date')
    title = request.form.get('title')
    amount = request.form.get('amount')
    category = request.form.get('category')

    try:
        datetime.strptime(date, '%Y-%m-%d')
        amount = float(amount)
        if not title or not category:
            raise ValueError("Title and category are required")

        with sqlite3.connect('transactions.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (date, title, amount, category)
                VALUES (?, ?, ?, ?)
            ''', (date, title, amount, category))
            conn.commit()
    except ValueError:
        pass

    return redirect(url_for('manage'))

@app.route('/update/<int:id>', methods=['POST'])
def update_transaction(id):
    date = request.form.get('date')
    title = request.form.get('title')
    amount = request.form.get('amount')
    category = request.form.get('category')

    try:
        datetime.strptime(date, '%Y-%m-%d')
        amount = float(amount)
        if not title or not category:
            raise ValueError("Title and category are required")

        with sqlite3.connect('transactions.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE transactions
                SET date = ?, title = ?, amount = ?, category = ?
                WHERE id = ?
            ''', (date, title, amount, category, id))
            conn.commit()
    except ValueError:
        pass

    return redirect(url_for('manage'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    with sqlite3.connect('transactions.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id = ?', (id,))
        conn.commit()
    return redirect(url_for('manage'))

@app.route('/chart-data', methods=['POST'])
def chart_data():
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')

    query = 'SELECT category, SUM(amount) FROM transactions WHERE LOWER(category) != ?'
    params = ['income']
    if start_date and end_date:
        query += ' AND date BETWEEN ? AND ?'
        params.extend([start_date, end_date])
    query += ' GROUP BY category'

    with sqlite3.connect('transactions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()

    labels = [row[0] for row in data]
    amounts = [row[1] for row in data]
    return jsonify({'labels': labels, 'amounts': amounts})

@app.route('/balance', methods=['GET', 'POST'])
def balance():
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')

    with sqlite3.connect('transactions.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(amount) FROM transactions WHERE LOWER(category) = ?', ('income',))
        income = cursor.fetchone()[0] or 0.0
        cursor.execute('SELECT SUM(amount) FROM transactions WHERE LOWER(category) != ?', ('income',))
        expenses = cursor.fetchone()[0] or 0.0
        balance = income - expenses

    return render_template('balance.html', balance=balance, start_date=start_date, end_date=end_date)

@app.route('/wealth-data', methods=['POST'])
def wealth_data():
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')

    query = 'SELECT date, SUM(amount) FROM transactions WHERE LOWER(category) = ?'
    params = ['income']
    if start_date and end_date:
        query += ' AND date BETWEEN ? AND ?'
        params.extend([start_date, end_date])
    query += ' GROUP BY date ORDER BY date'

    with sqlite3.connect('transactions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()

    labels = [row[0] for row in data]
    amounts = [row[1] for row in data]
    cumulative = []
    total = 0
    for amount in amounts:
        total += amount
        cumulative.append(total)

    return jsonify({'labels': labels, 'amounts': cumulative})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)