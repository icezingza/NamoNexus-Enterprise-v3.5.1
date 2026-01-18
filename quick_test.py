#!/usr/bin/env python3
"""Quick test to check if main modules load without errors."""

import sys
import traceback

try:
    print("Loading environment...")
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Environment loaded")
    
    print("\nLoading main modules...")
    from src.database.db import Base, get_db
    print("[OK] Database module loaded")
    
    from src.models.user import UserDB
    from src.models.interaction import InteractionDB
    from src.models.memory import MemoryDB
    print("[OK] Models loaded")
    
    print("\nAll modules loaded successfully!")
    sys.exit(0)
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
