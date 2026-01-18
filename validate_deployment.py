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
    """Check environment variables."""
    print("Checking environment variables...")
    
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
            errors.append(f"Missing required: {var}")
        elif len(value) < 32:
            warnings.append(f"Warning: {var} too short (< 32 chars)")
        elif var in ["NAMO_NEXUS_TOKEN", "DB_CIPHER_KEY"] and value == "YOUR_TOKEN_HERE":
            errors.append(f"Placeholder value still set for {var}")
    
    if os.getenv("NAMO_NEXUS_TOKEN") == os.getenv("DB_CIPHER_KEY"):
        warnings.append("Warning: token and cipher key are identical")
    
    return errors, warnings

def check_files_exist():
    """Check required files."""
    print("Checking required files...")
    
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
            errors.append(f"Missing file: {file}")
    
    return errors

def check_system_dependencies():
    """Check system dependencies (Linux/macOS only)."""
    print("Checking system dependencies...")
    
    errors = []
    warnings = []
    
    # Linux/macOS only
    if sys.platform in ['linux', 'darwin']:
        try:
            result = subprocess.run(
                ['pkg-config', '--modversion', 'sqlcipher'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                errors.append("sqlcipher not installed (run: apt-get install libsqlcipher-dev)")
            else:
                print(f"sqlcipher version: {result.stdout.strip()}")
        except FileNotFoundError:
            errors.append("pkg-config not found")
    
    return errors, warnings

def check_database():
    """Check database readiness."""
    print("Checking database...")
    
    errors = []
    warnings = []
    
    db_path = os.getenv("DB_PATH", "namo_nexus_sovereign.db")
    
    if Path(db_path).exists():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"Database found with tables: {tables}")

            # Size check
            size_mb = Path(db_path).stat().st_size / (1024 * 1024)
            if size_mb > 1000:
                warnings.append(f"Warning: DB size large: {size_mb:.1f} MB")
            
            conn.close()
        except Exception as e:
            errors.append(f"DB error: {e}")
    else:
        warnings.append(f"Warning: DB not found, will be created: {db_path}")
    
    return errors, warnings

def check_tests():
    """Check test setup."""
    print("Checking tests...")
    
    errors = []
    warnings = []
    
    if not Path("tests").exists():
        errors.append("Tests directory not found")
        return errors, warnings
    
    # Check whether pytest is installed.
    try:
        import pytest
    except ImportError:
        warnings.append("Warning: pytest not installed (pip install pytest)")
    
    return errors, warnings

def main():
    print("=" * 70)
    print("NamoNexus Enterprise v3.5.1 - Deployment Validation")
    print("=" * 70)
    print()
    
    all_errors = []
    all_warnings = []
    
    # Run all checks.
    env_errors, env_warnings = check_environment_variables()
    file_errors = check_files_exist()
    sys_errors, sys_warnings = check_system_dependencies()
    db_errors, db_warnings = check_database()
    test_errors, test_warnings = check_tests()
    
    all_errors.extend(env_errors + file_errors + sys_errors + db_errors + test_errors)
    all_warnings.extend(env_warnings + sys_warnings + db_warnings + test_warnings)
    
    # Print summary
    print()
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    
    if all_errors:
        print(f"\nErrors found ({len(all_errors)}):")
        for error in all_errors:
            print(f"   {error}")
    
    if all_warnings:
        print(f"\nWarnings found ({len(all_warnings)}):")
        for warning in all_warnings:
            print(f"   {warning}")
    
    if not all_errors and not all_warnings:
        print("\nAll checks passed. System ready for deployment.")
        return 0
    elif not all_errors:
        print("\nNo critical errors. Address warnings before deployment.")
        return 0
    else:
        print(f"\n{len(all_errors)} critical errors must be fixed before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
