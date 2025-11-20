#!/usr/bin/env python3
"""
Generate SHA-256 hash for admin password
"""

import hashlib
from db_manager import get_db

def generate_password_hash(password: str) -> str:
    """Generate SHA-256 hash of password."""
    return hashlib.sha256(password.encode()).hexdigest()

def update_admin_password(new_password: str):
    """Update admin password in database."""
    try:
        db = get_db()
        success, message = db.update_admin_password(new_password)
        
        if success:
            password_hash = generate_password_hash(new_password)
            print("✓ Password admin berhasil diupdate!")
            print(f"  Hash: {password_hash}")
        else:
            print(f"✗ Error: {message}")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("Generate Admin Password Hash")
    print("=" * 50)
    print()
    
    # Option 1: Just generate hash
    print("Pilihan 1: Generate hash saja")
    password = input("Masukkan password: ")
    hash_value = generate_password_hash(password)
    print(f"\nSHA-256 Hash: {hash_value}")
    print()
    
    # Option 2: Update companies.json
    print("-" * 50)
    print("Pilihan 2: Update companies.json langsung")
    update = input("Update companies.json? (y/n): ").lower()
    
    if update == 'y':
        new_password = input("Masukkan password baru: ")
        confirm_password = input("Konfirmasi password: ")
        
        if new_password == confirm_password:
            update_admin_password(new_password)
        else:
            print("✗ Password tidak cocok!")
    
    print()
    print("=" * 50)
