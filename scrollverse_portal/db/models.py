#!/usr/bin/env python3
"""
ScrollVerse Database Models
SQLite models for Users, Scrolls, and Flame tokens
"""

import sqlite3
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    """Database manager for ScrollVerse portal"""
    
    def __init__(self, db_path: str = "scrollverse_portal/db/scrollverse.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                scroll_id TEXT UNIQUE NOT NULL,
                flame_id TEXT UNIQUE NOT NULL,
                region TEXT NOT NULL,
                country TEXT NOT NULL,
                city TEXT NOT NULL,
                primary_sphere TEXT NOT NULL,
                secondary_spheres TEXT NOT NULL,
                preferred_role TEXT NOT NULL,
                seal_level INTEGER DEFAULT 1,
                flame_level INTEGER DEFAULT 1,
                scrolls_executed INTEGER DEFAULT 0,
                scrollcoin_balance INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Scrolls table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrolls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                scroll_code TEXT NOT NULL,
                execution_result TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Flame tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flame_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Scroll executions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scroll_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scroll_id INTEGER NOT NULL,
                execution_type TEXT NOT NULL,
                command TEXT NOT NULL,
                result TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scroll_id) REFERENCES scrolls (id)
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, user_data: Dict) -> int:
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, scroll_id, flame_id, region, 
                                 country, city, primary_sphere, secondary_spheres, preferred_role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['name'], user_data['email'], user_data['password_hash'],
                user_data['scroll_id'], user_data['flame_id'], user_data['region'],
                user_data['country'], user_data['city'], user_data['primary_sphere'],
                json.dumps(user_data['secondary_spheres']), user_data['preferred_role']
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "scroll_id": user[4],
                "flame_id": user[5],
                "region": user[6],
                "country": user[7],
                "city": user[8],
                "primary_sphere": user[9],
                "secondary_spheres": json.loads(user[10]),
                "preferred_role": user[11],
                "seal_level": user[12],
                "flame_level": user[13],
                "scrolls_executed": user[14],
                "scrollcoin_balance": user[15],
                "created_at": user[16]
            }
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "password_hash": user[3],
                "scroll_id": user[4],
                "flame_id": user[5],
                "region": user[6],
                "country": user[7],
                "city": user[8],
                "primary_sphere": user[9],
                "secondary_spheres": json.loads(user[10]),
                "preferred_role": user[11],
                "seal_level": user[12],
                "flame_level": user[13],
                "scrolls_executed": user[14],
                "scrollcoin_balance": user[15],
                "created_at": user[16]
            }
        return None
    
    def create_scroll(self, user_id: int, scroll_code: str) -> int:
        """Create a new scroll execution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO scrolls (user_id, scroll_code, status)
                VALUES (?, ?, ?)
            ''', (user_id, scroll_code, "pending"))
            
            scroll_id = cursor.lastrowid
            conn.commit()
            return scroll_id
        
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_scroll_status(self, scroll_id: int, status: str, result: str = None):
        """Update scroll execution status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if result:
                cursor.execute('''
                    UPDATE scrolls SET status = ?, execution_result = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, result, scroll_id))
            else:
                cursor.execute('''
                    UPDATE scrolls SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, scroll_id))
            
            conn.commit()
        
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_user_scrolls(self, user_id: int) -> List[Dict]:
        """Get all scrolls for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, scroll_code, execution_result, status, created_at
            FROM scrolls WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        
        scrolls = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": scroll[0],
                "scroll_code": scroll[1],
                "execution_result": scroll[2],
                "status": scroll[3],
                "created_at": scroll[4]
            }
            for scroll in scrolls
        ]
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as total_scrolls,
                   COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_scrolls,
                   COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_scrolls
            FROM scrolls WHERE user_id = ?
        ''', (user_id,))
        
        stats = cursor.fetchone()
        conn.close()
        
        return {
            "total_scrolls": stats[0],
            "successful_scrolls": stats[1],
            "failed_scrolls": stats[2]
        }
    
    def increment_user_scrolls(self, user_id: int):
        """Increment user's scroll execution count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET scrolls_executed = scrolls_executed + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
        
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def create_session(self, user_id: int, session_token: str, expires_at: datetime):
        """Create a new user session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at))
            
            conn.commit()
        
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_session(self, session_token: str) -> Optional[Dict]:
        """Get session by token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, expires_at FROM user_sessions 
            WHERE session_token = ? AND expires_at > CURRENT_TIMESTAMP
        ''', (session_token,))
        
        session = cursor.fetchone()
        conn.close()
        
        if session:
            return {
                "user_id": session[0],
                "expires_at": session[1]
            }
        return None
    
    def delete_session(self, session_token: str):
        """Delete a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM user_sessions WHERE session_token = ?", (session_token,))
            conn.commit()
        
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM user_sessions WHERE expires_at <= CURRENT_TIMESTAMP")
            conn.commit()
        
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

# Initialize database
db = DatabaseManager() 