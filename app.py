# app.py

import os
import sqlite3
import csv
from flask import Flask, render_template, request, g, flash, redirect, url_for, send_file

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace 'your_secret_key_here' with your actual secret key.

DATABASE = os.path.join(app.root_path, 'transactions.db')

# Database initialization and connection management
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Create the database table
def create_table():
    with app.app_context():
        conn = get_db()
        conn.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        particulars TEXT NOT NULL,
                        amount REAL NOT NULL,
                        transaction_type TEXT NOT NULL,
                        date_time TEXT NOT NULL
                        )''')
        conn.commit()

# Home page to add transactions
@app.route('/', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        category = request.form['category']
        particulars = request.form['particulars']
        amount = float(request.form['amount'])
        transaction_type = request.form['transaction_type']
        date_time = request.form['date_time']

        conn = get_db()
        conn.execute(
            'INSERT INTO transactions (category, particulars, amount, transaction_type, date_time) VALUES (?, ?, ?, ?, ?)',
            (category, particulars, amount, transaction_type, date_time)
        )
        conn.commit()

        flash('Transaction added successfully.', 'success')

    with app.app_context():
        conn = get_db()
        cur = conn.execute('SELECT * FROM transactions WHERE transaction_type="Income"')
        incomes = cur.fetchall()
        cur = conn.execute('SELECT * FROM transactions WHERE transaction_type="Expense"')
        expenses = cur.fetchall()

        income_total = sum(income[3] for income in incomes)  # Access the 'amount' field using integer index 3
        expense_total = sum(expense[3] for expense in expenses)  # Access the 'amount' field using integer index 3
        current_balance = income_total - expense_total

    current_datetime = None
    return render_template('add_transaction.html', current_balance=current_balance, current_datetime=current_datetime)


    return render_template('add_transaction.html', current_balance=current_balance, current_datetime=current_datetime)
# View transactions
@app.route('/view_transactions')
def view_transactions():
    with app.app_context():
        conn = get_db()
        cur = conn.execute('SELECT * FROM transactions ORDER BY date_time DESC')
        transactions = cur.fetchall()

    return render_template('view_transactions.html', transactions=transactions)

# Edit transaction
@app.route('/edit_transaction/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    conn = get_db()
    cur = conn.execute('SELECT * FROM transactions WHERE id=?', (id,))
    transaction = cur.fetchone()

    if request.method == 'POST':
        category = request.form['category']
        particulars = request.form['particulars']
        amount = float(request.form['amount'])
        transaction_type = request.form['transaction_type']
        date_time = request.form['date_time']

        conn.execute(
            'UPDATE transactions SET category=?, particulars=?, amount=?, transaction_type=?, date_time=? WHERE id=?',
            (category, particulars, amount, transaction_type, date_time, id)
        )
        conn.commit()

        flash('Transaction updated successfully.', 'success')

        return redirect(url_for('view_transactions'))

    return render_template('edit_transaction.html', transaction=transaction)

# Export transactions to CSV
# app.py

# ... (previous code)

@app.route('/export', methods=['GET'])
def export_to_csv():
    conn = get_db()
    cur = conn.execute('SELECT * FROM transactions')
    transactions = cur.fetchall()

    with open('transactions.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Date', 'Category', 'Particulars', 'Amount', 'Transaction Type'])
        for data in transactions:
            writer.writerow([data[0], data[1], data[2], data[3], data[4], data[5]])

    return send_file('transactions.csv', as_attachment=True)

# ... (rest of the code)


if __name__ == '__main__':
    create_table()  # Create the database table before running the app
    app.run(debug=True)
