from flask import Flask, request, render_template, redirect, url_for, flash, session, Blueprint, jsonify
import sqlite3
import threading
from flask_socketio import emit
import cv2
from .face.face_authen import add_new_user_data
from .socket import socketio

main_bp = Blueprint('main', __name__)


def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@main_bp.route('/')
def home():
    return render_template('index.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        print(session)
        if user:
            session['user'] = username  # Save user info in session
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
        
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insert the new user into the database
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            
            conn.commit()
            cursor.execute("SELECT MAX(id) FROM users")
            last_user_id = cursor.fetchone()[0]  # Fetch the max user_id
            conn.commit()
            flash('Registration successful! You can now log in.', 'success')
            add_new_user_data(last_user_id)
            return redirect(url_for('main.login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'danger')
        finally:
            conn.close()
            
        
        
    return render_template('register.html')

@main_bp.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"Welcome, {session['user']}! <a href='/logout'>Logout</a>"
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('main.login'))
    
    
@main_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@main_bp.route('/face_login')
def test():
    return render_template('face_login.html')

@main_bp.route('/set_session', methods=['POST'])
def set_session():
    data = request.json  # Expecting JSON data
    if 'username' in data:
        session['user'] = data['username']
        session.modified = True
        return jsonify({"message": "Session set successfully"}), 200
    return jsonify({"message": "Invalid data"}), 400
