import sqlite3
import asyncio
import threading
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import os


class DatabaseManager:
    def __init__(self, db_path: str = "forelka.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn = None
        self._init_tables()
    
    def _init_tables(self):
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    api_id TEXT NOT NULL,
                    api_hash TEXT NOT NULL,
                    prefix TEXT DEFAULT '.',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS owners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    owner_id INTEGER NOT NULL,
                    is_admin BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE,
                    UNIQUE(account_id, owner_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE,
                    UNIQUE(account_id, key)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS modules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    module_name TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    version TEXT,
                    developer TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE,
                    UNIQUE(account_id, module_name)
                )
            """)
            
            conn.commit()
            conn.close()
    
    async def initialize(self):
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
    
    async def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
    
    @asynccontextmanager
    async def get_cursor(self):
        if not self._conn:
            await self.initialize()
        
        cursor = self._conn.cursor()
        try:
            yield cursor
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cursor.close()
    
    async def add_account(self, user_id: int, api_id: str, api_hash: str, prefix: str = ".") -> int:
        async with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO accounts (user_id, api_id, api_hash, prefix)
                VALUES (?, ?, ?, ?)
            """, (user_id, api_id, api_hash, prefix))
            return cursor.lastrowid
    
    async def get_account_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        async with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM accounts WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    async def get_account_by_id(self, account_id: int) -> Optional[Dict[str, Any]]:
        async with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    async def get_all_accounts(self) -> List[Dict[str, Any]]:
        async with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM accounts")
            return [dict(row) for row in cursor.fetchall()]
    
    async def remove_account(self, account_id: int):
        async with self.get_cursor() as cursor:
            cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    
    async def add_owner(self, account_id: int, owner_id: int, is_admin: bool = False):
        async with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO owners (account_id, owner_id, is_admin)
                VALUES (?, ?, ?)
            """, (account_id, owner_id, is_admin))
    
    async def remove_owner(self, account_id: int, owner_id: int):
        async with self.get_cursor() as cursor:
            cursor.execute("""
                DELETE FROM owners WHERE account_id = ? AND owner_id = ?
            """, (account_id, owner_id))
    
    async def get_owners(self, account_id: int) -> List[int]:
        async with self.get_cursor() as cursor:
            cursor.execute("SELECT owner_id FROM owners WHERE account_id = ?", (account_id,))
            return [row[0] for row in cursor.fetchall()]
    
    async def is_owner(self, account_id: int, user_id: int) -> bool:
        async with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM owners WHERE account_id = ? AND owner_id = ?
            """, (account_id, user_id))
            return cursor.fetchone() is not None
    
    async def set_setting(self, account_id: int, key: str, value: Any):
        async with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO settings (account_id, key, value, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (account_id, key, str(value)))
    
    async def get_setting(self, account_id: int, key: str, default: Any = None) -> Any:
        async with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT value FROM settings WHERE account_id = ? AND key = ?
            """, (account_id, key))
            row = cursor.fetchone()
            return row[0] if row else default
    
    async def get_all_settings(self, account_id: int) -> Dict[str, Any]:
        async with self.get_cursor() as cursor:
            cursor.execute("SELECT key, value FROM settings WHERE account_id = ?", (account_id,))
            return {row[0]: row[1] for row in cursor.fetchall()}
    
    async def register_module(self, account_id: int, module_name: str, version: str = "1.0", 
                            developer: str = "Unknown", description: str = ""):
        async with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO modules (account_id, module_name, version, developer, description, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (account_id, module_name, version, developer, description))
    
    async def enable_module(self, account_id: int, module_name: str):
        async with self.get_cursor() as cursor:
            cursor.execute("""
                UPDATE modules SET enabled = 1 WHERE account_id = ? AND module_name = ?
            """, (account_id, module_name))
    
    async def disable_module(self, account_id: int, module_name: str):
        async with self.get_cursor() as cursor:
            cursor.execute("""
                UPDATE modules SET enabled = 0 WHERE account_id = ? AND module_name = ?
            """, (account_id, module_name))
    
    async def get_enabled_modules(self, account_id: int) -> List[str]:
        async with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT module_name FROM modules WHERE account_id = ? AND enabled = 1
            """, (account_id,))
            return [row[0] for row in cursor.fetchall()]
    
    async def get_module_info(self, account_id: int, module_name: str) -> Optional[Dict[str, Any]]:
        async with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM modules WHERE account_id = ? AND module_name = ?
            """, (account_id, module_name))
            row = cursor.fetchone()
            return dict(row) if row else None