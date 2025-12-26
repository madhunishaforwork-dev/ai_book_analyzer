
import sqlite3
import hashlib
import os
import uuid
from datetime import datetime
import streamlit as st

DB_FILE = "user_data/users.db"

class AuthManager:
    def __init__(self):
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database for users."""
        os.makedirs("user_data", exist_ok=True)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                password_hash TEXT,
                role TEXT,
                created_at TEXT,
                last_login TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _hash_password(self, password):
        """Simple SHA-256 hashing (for demo purposes; assume bcrypt in prod)."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, email, password, role="Registered"):
        """Registers a new user."""
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Check existing
            c.execute("SELECT email FROM users WHERE email=?", (email,))
            if c.fetchone():
                return False, "Email already registered."
            
            user_id = str(uuid.uuid4())
            pwd_hash = self._hash_password(password)
            created_at = datetime.now().isoformat()
            
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                      (user_id, email, pwd_hash, role, created_at, created_at))
            conn.commit()
            conn.close()
            return True, "Registration successful! Please login."
        except Exception as e:
            return False, str(e)

    def login_user(self, email, password):
        """Authenticates user."""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        pwd_hash = self._hash_password(password)
        c.execute("SELECT id, role, email FROM users WHERE email=? AND password_hash=?", (email, pwd_hash))
        user = c.fetchone()
        
        if user:
            # Update last login
            c.execute("UPDATE users SET last_login=? WHERE id=?", (datetime.now().isoformat(), user[0]))
            conn.commit()
            conn.close()
            return {
                "id": user[0],
                "role": user[1],
                "email": user[2],
                "is_authenticated": True
            }
        
        conn.close()
        return None

    def guest_login(self):
        """Returns a guest session."""
        return {
            "id": "guest_user",
            "role": "Guest",
            "email": "guest@example.com",
            "is_authenticated": True
        }
