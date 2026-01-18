#!/usr/bin/env python3
"""
Validate NamoNexus Enterprise v3.5.1 deployment readiness
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path

def check_environment_variables():
    """ตรวจสอบ environment variables"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        "NAMO_NEXUS_TOKEN",
        "DB_CIPHER_KEY",
        "DATABASE_URL",
    ]
    
    warnings = []
    errors = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            errors.append(f"❌ Missing required: {var}")
        elif len(value) < 32:
            warnings.append(f"⚠️  {var} too short (< 32 chars)")
        elif var in ["NAMO_NEXUS_TOKEN", "DB_CIPHER_KEY"] and value == "YOUR_TOKEN_HERE":
            errors.append(f"❌ {var} ยังใช้ค่า placeholder")
    
    if os.getenv("NAMO_NEXUS_TOKEN") == os.getenv("DB_CIPHER_KEY"):
        warnings.append("⚠️  Token และ Cipher Key เป็นค่าเดียวกัน")
    
    return errors, warnings

def check_files_exist():
    """ตรวจสอบไฟล์สำคัญ"""
    print("🔍 Checking required files...")
    
    required_files = [
        "main.py",
        "database.py",
        "core_engine.py",
        ".env",
        "alembic.ini",
        "docker-compose.yml",
        "requirements.txt"
    ]
    
    errors = []
    for file in required_files:
        if not Path(file).exists():
            errors.append(f"❌ Missing file: {file}")
    
    return errors

def check_system_dependencies():
    """ตรวจสอบ system dependencies (Linux/macOS only)"""
    print("🔍 Checking system dependencies...")
    
    errors = []
    warnings = []
    
    # ตรวจสอบเฉพาะ Linux/macOS
    if sys.platform in ['linux', 'darwin']:
        try:
            result = subprocess.run(
                ['pkg-config', '--modversion', 'sqlcipher'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                errors.append("❌ sqlcipher not installed (run: apt-get install libsqlcipher-dev)")
            else:
                print(f"✅ sqlcipher version: {result.stdout.strip()}")
        except FileNotFoundError:
            errors.append("❌ pkg-config not found")
    
    return errors, warnings

def check_database():
    """ตรวจสอบฐานข้อมูล"""
    print("🔍 Checking database...")
    
    errors = []
    warnings = []
    
    db_path = os.getenv("DB_PATH", "namo_nexus_sovereign.db")
    
    if Path(db_path).exists():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"✅ DB found with tables: {tables}")
            
            # เช็คขนาด
            size_mb = Path(db_path).stat().st_size / (1024 * 1024)
            if size_mb > 1000:
                warnings.append(f"⚠️  DB size large: {size_mb:.1f} MB")
            
            conn.close()
        except Exception as e:
            errors.append(f"❌ DB error: {e}")
    else:
        warnings.append(f"⚠️  DB not found, will be created: {db_path}")
    
    return errors, warnings

def check_tests():
    """ตรวจสอบว่า tests พร้อม"""
    print("🔍 Checking tests...")
    
    errors = []
    
    if not Path("tests").exists():
        errors.append("❌ Tests directory not found")
        return errors
    
    # ตรวจสอบว่า pytest ติดตั้งหรือไม่
    try:
        import pytest
    except ImportError:
        warnings.append("⚠️  pytest not installed (pip install pytest)")
    
    return errors

def main():
    print("=" * 70)
    print("NamoNexus Enterprise v3.5.1 - Deployment Validation")
    print("=" * 70)
    print()
    
    all_errors = []
    all_warnings = []
    
    # รัน checks ทั้งหมด
    env_errors, env_warnings = check_environment_variables()
    file_errors = check_files_exist()
    sys_errors, sys_warnings = check_system_dependencies()
    db_errors, db_warnings = check_database()
    test_errors = check_tests()
    
    all_errors.extend(env_errors + file_errors + sys_errors + db_errors + test_errors)
    all_warnings.extend(env_warnings + sys_warnings + db_warnings)
    
    # แสดงผลสรุป
    print()
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    
    if all_errors:
        print(f"\n🔴 Errors found ({len(all_errors)}):")
        for error in all_errors:
            print(f"   {error}")
    
    if all_warnings:
        print(f"\n⚠️  Warnings found ({len(all_warnings)}):")
        for warning in all_warnings:
            print(f"   {warning}")
    
    if not all_errors and not all_warnings:
        print("\n✅ All checks passed! System ready for deployment.")
        return 0
    elif not all_errors:
        print("\n✅ No critical errors. Address warnings before deployment.")
        return 0
    else:
        print(f"\n❌ {len(all_errors)} critical errors must be fixed before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
