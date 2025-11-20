#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Manager for Coretax Extractor
Handles SQLite database operations for companies and admin
"""

import sqlite3
import hashlib
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class DatabaseManager:
    """Manage SQLite database for companies and admin."""
    
    def __init__(self, db_path: str = "coretax.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database with tables and default data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create companies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                npwp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create admin table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create app settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT NOT NULL UNIQUE,
                setting_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if admin exists, if not create default
        cursor.execute("SELECT COUNT(*) FROM admin")
        if cursor.fetchone()[0] == 0:
            default_password_hash = hashlib.sha256("admin".encode()).hexdigest()
            cursor.execute(
                "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
                ("admin", default_password_hash)
            )
            self._log_action(cursor, "ADMIN_CREATED", "Default admin account created")
        
        # Check if app password exists, if not create default
        cursor.execute("SELECT COUNT(*) FROM app_settings WHERE setting_key = 'app_password'")
        if cursor.fetchone()[0] == 0:
            default_app_password_hash = hashlib.sha256("indonesia123".encode()).hexdigest()
            cursor.execute(
                "INSERT INTO app_settings (setting_key, setting_value) VALUES (?, ?)",
                ("app_password", default_app_password_hash)
            )
            self._log_action(cursor, "APP_PASSWORD_CREATED", "Default app password created")
        
        # Check if companies exist, if not add defaults
        cursor.execute("SELECT COUNT(*) FROM companies")
        if cursor.fetchone()[0] == 0:
            default_companies = [
                ("KAP  Amir Abadi Jusuf Aryanto Mawar & Rekan", "19010669038000"),
                ("RSM Indonesia Konsultan", "15659428012000"),
                ("RSM Indonesia Mitradaya", "663243616012000"),
                ("RSM Indonesia Mitradana", "706120862012000"),
                ("AAJ Indonesia", "29143286012000"),
                ("RSM Indonesia Advisory", "21486899012000"),
                ("AAJ Kapital", "32114993012000"),
                ("Srihana Utama", "13728076038000"),
                ("Amandamai Arthakita Jagaselama", "19008572012000"),
                ("Sapta Abdi Dharma", "946892767012000"),
            ]
            
            cursor.executemany(
                "INSERT INTO companies (name, npwp) VALUES (?, ?)",
                default_companies
            )
            self._log_action(cursor, "COMPANIES_INITIALIZED", f"Added {len(default_companies)} default companies")
        
        conn.commit()
        conn.close()
    
    def _log_action(self, cursor, action: str, details: str = ""):
        """Log action to audit log."""
        cursor.execute(
            "INSERT INTO audit_log (action, details) VALUES (?, ?)",
            (action, details)
        )
    
    def get_all_companies(self) -> Dict[str, str]:
        """Get all companies as dict {name: npwp}."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, npwp FROM companies ORDER BY name")
        companies = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return companies
    
    def get_company_by_name(self, name: str) -> Optional[Tuple[str, str]]:
        """Get company by name."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, npwp FROM companies WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        conn.close()
        return result
    
    def add_company(self, name: str, npwp: str) -> Tuple[bool, str]:
        """Add new company. Returns (success, message)."""
        # Validation
        if not name or not name.strip():
            return False, "Nama perusahaan tidak boleh kosong"
        
        if not npwp or not npwp.strip():
            return False, "NPWP tidak boleh kosong"
        
        npwp = npwp.strip()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if company already exists
            cursor.execute("SELECT COUNT(*) FROM companies WHERE name = ?", (name,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return False, "Perusahaan sudah ada dalam daftar"
            
            # Insert company
            cursor.execute(
                "INSERT INTO companies (name, npwp) VALUES (?, ?)",
                (name, npwp)
            )
            
            # Log action
            self._log_action(cursor, "COMPANY_ADDED", f"Added company: {name} (NPWP: {npwp})")
            
            conn.commit()
            conn.close()
            
            return True, f"Perusahaan '{name}' berhasil ditambahkan"
            
        except sqlite3.IntegrityError:
            return False, "Perusahaan sudah ada dalam daftar"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def delete_company(self, name: str) -> Tuple[bool, str]:
        """Delete company. Returns (success, message)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if company exists
            cursor.execute("SELECT COUNT(*) FROM companies WHERE name = ?", (name,))
            if cursor.fetchone()[0] == 0:
                conn.close()
                return False, "Perusahaan tidak ditemukan"
            
            # Delete company
            cursor.execute("DELETE FROM companies WHERE name = ?", (name,))
            
            # Log action
            self._log_action(cursor, "COMPANY_DELETED", f"Deleted company: {name}")
            
            conn.commit()
            conn.close()
            
            return True, f"Perusahaan '{name}' berhasil dihapus"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def update_company(self, old_name: str, new_name: str, new_npwp: str) -> Tuple[bool, str]:
        """Update company. Returns (success, message)."""
        # Validation
        if not new_name or not new_name.strip():
            return False, "Nama perusahaan tidak boleh kosong"
        
        if not new_npwp or not new_npwp.strip():
            return False, "NPWP tidak boleh kosong"
        
        new_npwp = new_npwp.strip()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update company
            cursor.execute(
                "UPDATE companies SET name = ?, npwp = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                (new_name, new_npwp, old_name)
            )
            
            if cursor.rowcount == 0:
                conn.close()
                return False, "Perusahaan tidak ditemukan"
            
            # Log action
            self._log_action(cursor, "COMPANY_UPDATED", f"Updated company: {old_name} -> {new_name}")
            
            conn.commit()
            conn.close()
            
            return True, f"Perusahaan berhasil diupdate"
            
        except sqlite3.IntegrityError:
            return False, "Nama perusahaan sudah digunakan"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def verify_admin_password(self, password: str) -> bool:
        """Verify admin password."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT password_hash FROM admin WHERE username = ?", ("admin",))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                stored_hash = result[0]
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                return password_hash == stored_hash
            
            return False
            
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False
    
    def get_admin_username(self) -> str:
        """Get current admin username."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT username FROM admin LIMIT 1")
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] if result else "admin"
            
        except Exception as e:
            print(f"Error getting username: {e}")
            return "admin"
    
    def update_admin_username(self, new_username: str) -> Tuple[bool, str]:
        """Update admin username. Returns (success, message)."""
        if not new_username or len(new_username) < 3:
            return False, "Username minimal 3 karakter"
        
        if not new_username.replace('_', '').replace('-', '').isalnum():
            return False, "Username hanya boleh huruf, angka, underscore, dan dash"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get old username for logging
            cursor.execute("SELECT username FROM admin LIMIT 1")
            old_username = cursor.fetchone()[0]
            
            cursor.execute(
                "UPDATE admin SET username = ?, updated_at = CURRENT_TIMESTAMP",
                (new_username,)
            )
            
            # Log action
            self._log_action(cursor, "USERNAME_CHANGED", f"Admin username changed from '{old_username}' to '{new_username}'")
            
            conn.commit()
            conn.close()
            
            return True, "Username berhasil diupdate"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def update_admin_password(self, new_password: str) -> Tuple[bool, str]:
        """Update admin password. Returns (success, message)."""
        if not new_password or len(new_password) < 4:
            return False, "Password minimal 4 karakter"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            
            cursor.execute(
                "UPDATE admin SET password_hash = ?, updated_at = CURRENT_TIMESTAMP",
                (password_hash,)
            )
            
            # Log action
            self._log_action(cursor, "PASSWORD_CHANGED", "Admin password updated")
            
            conn.commit()
            conn.close()
            
            return True, "Password berhasil diupdate"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_audit_log(self, limit: int = 100) -> List[Tuple]:
        """Get audit log entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT action, details, timestamp FROM audit_log ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        logs = cursor.fetchall()
        
        conn.close()
        return logs
    
    def verify_app_password(self, password: str) -> bool:
        """Verify application password."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT setting_value FROM app_settings WHERE setting_key = 'app_password'")
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                stored_hash = result[0]
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                return password_hash == stored_hash
            
            return False
            
        except Exception as e:
            print(f"Error verifying app password: {e}")
            return False
    
    def update_app_password(self, new_password: str) -> Tuple[bool, str]:
        """Update application password. Returns (success, message)."""
        if not new_password or len(new_password) < 4:
            return False, "Password minimal 4 karakter"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            
            cursor.execute(
                "UPDATE app_settings SET setting_value = ?, updated_at = CURRENT_TIMESTAMP WHERE setting_key = 'app_password'",
                (password_hash,)
            )
            
            # Log action
            self._log_action(cursor, "APP_PASSWORD_CHANGED", "Application password updated")
            
            conn.commit()
            conn.close()
            
            return True, "Password aplikasi berhasil diupdate"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM companies")
        company_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM audit_log")
        log_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT created_at FROM companies ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        last_company_added = result[0] if result else "N/A"
        
        conn.close()
        
        return {
            "total_companies": company_count,
            "total_logs": log_count,
            "last_company_added": last_company_added,
        }


# Singleton instance
_db_instance = None

def get_db() -> DatabaseManager:
    """Get database manager singleton instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
