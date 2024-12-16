from flask import Flask
import sqlite3
import os
from flask_session import Session
from .socket import socketio

from .auth import Auth
from .routes import main_bp

#socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    app.config['SESSION_COOKIE_NAME'] = 'your_session_cookie_name'
    app.config['SESSION_COOKIE_PATH'] = '/'
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # Configure Flask to use server-side sessions (filesystem in this case)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure key
    Session(app)  # Initialize Flask-Session
    
    app.secret_key = 'hay_lam_dmm'  # Change this to a secure key
    init_db()
    # Initialize authentication module
    app.register_blueprint(Auth)
    app.register_blueprint(main_bp)

    socketio.init_app(app)
    return app

def init_db():
    db_path = 'users.db'
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create the users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        # Insert sample data
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('user1', 'password123'))
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('user2', 'secure456'))

        conn.commit()
        conn.close()
