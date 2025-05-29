from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import re

app = Flask(__name__)
app.secret_key = "your_secret_key"
DB_NAME = "users.db"

# Database initialize karne ka function
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                coins INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Password validation - backend
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        if not re.match(pattern, password):
            flash("Password must be at least 8 characters long, contain 1 uppercase, 1 lowercase letter and 1 number.", "danger")
            return render_template('register.html')

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username or Email already exists! Choose another.", "danger")
        finally:
            conn.close()
    return render_template('register.html')

# Login route
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash(f"Welcome {user[1]}!", "success")
            return redirect(url_for('main'))
        else:
            flash("Invalid credentials!", "danger")
    return render_template('login.html')

# Main page - coins and ads
@app.route('/main')
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT coins FROM users WHERE id=?", (user_id,))
    coins = c.fetchone()[0]
    conn.close()
    return render_template('main.html', coins=coins)

# Watch ad - add 10 coins
@app.route('/watch_ad')
def watch_ad():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins + 10 WHERE id=?", (user_id,))
    conn.commit()
    c.execute("SELECT coins FROM users WHERE id=?", (user_id,))
    coins = c.fetchone()[0]
    conn.close()
    flash("You earned 10 coins!", "success")
    return redirect(url_for('main'))

# Withdraw coins with UPI input and coin check
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT coins FROM users WHERE id=?", (user_id,))
    coins = c.fetchone()[0]

    if request.method == 'POST':
        if coins >= 2000:
            upi_id = request.form.get('upi_id')
            if not upi_id:
                flash("Please enter a valid UPI ID.", "danger")
                conn.close()
                return redirect(url_for('withdraw'))

            # Deduct coins
            new_coins = coins - 2000
            c.execute("UPDATE users SET coins=? WHERE id=?", (new_coins, user_id))
            conn.commit()
            flash(f"Withdrawal successful! 2000 coins deducted. Paid to UPI: {upi_id}", "success")
        else:
            flash("You need at least 2000 coins to withdraw.", "danger")
        conn.close()
        return redirect(url_for('main'))

    conn.close()
    return render_template('withdraw.html', coins=coins)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
