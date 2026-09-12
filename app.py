from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, init_db
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')

VALID_ROLES = ['farmer', 'fpo', 'consumer', 'bulk_buyer']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', '')

        if not name or not email or not password or not confirm_password or not role:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if role not in VALID_ROLES:
            flash('Invalid role selected.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE email = ?', (email,)
        ).fetchone()

        if existing_user:
            conn.close()
            flash('An account with this email already exists.', 'error')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)',
            (name, email, password_hash, role)
        )
        conn.commit()
        conn.close()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user is None or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.', 'error')
            return render_template('login.html')

        session.clear()
        session['user_id'] = user['id']
        session['name'] = user['name']
        session['role'] = user['role']

        flash(f'Welcome back, {user["name"]}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['name'], role=session['role'])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)