import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "emails.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purpose TEXT NOT NULL,
            recipient TEXT,
            user_name TEXT,
            tone TEXT NOT NULL,
            length TEXT,
            user_message TEXT NOT NULL,
            subject TEXT NOT NULL,
            greeting TEXT,
            body TEXT NOT NULL,
            closing TEXT,
            full_email TEXT NOT NULL,
            is_favorite BOOLEAN DEFAULT 0,
            version INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    # Safe migration check for missing columns if table existed from earlier version
    cursor.execute("PRAGMA table_info(email_history)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "user_name" not in columns:
        cursor.execute("ALTER TABLE email_history ADD COLUMN user_name TEXT")
    if "version" not in columns:
        cursor.execute("ALTER TABLE email_history ADD COLUMN version INTEGER DEFAULT 1")
    conn.commit()
    conn.close()

def save_email(
    purpose: str,
    recipient: str,
    tone: str,
    length: str,
    user_message: str,
    subject: str,
    greeting: str,
    body: str,
    closing: str,
    full_email: str,
    user_name: Optional[str] = "",
    version: int = 1
) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO email_history (purpose, recipient, user_name, tone, length, user_message, subject, greeting, body, closing, full_email, version)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (purpose, recipient, user_name or "", tone, length, user_message, subject, greeting, body, closing, full_email, version))
    conn.commit()
    email_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM email_history WHERE id = ?", (email_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def get_history(limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM email_history ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def toggle_favorite(email_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_favorite FROM email_history WHERE id = ?", (email_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    
    new_fav = 0 if row["is_favorite"] else 1
    cursor.execute("UPDATE email_history SET is_favorite = ? WHERE id = ?", (new_fav, email_id))
    conn.commit()
    conn.close()
    return bool(new_fav)

def delete_email(email_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM email_history WHERE id = ?", (email_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def clear_all_history() -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM email_history")
    conn.commit()
    conn.close()
    return True
