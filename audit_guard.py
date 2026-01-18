import os
import re
import sys

# 🎯 เป้าหมาย: สแกนหา "สิ่งต้องห้าม" ใน Code
FORBIDDEN_PATTERNS = {
    r'print\(': "❌ Found 'print()' statement (Use logging instead)",
    r'token\s*=\s*["\'][a-zA-Z0-9-]{10,}["\']': "❌ Found potential Hardcoded Token",
    r'key\s*=\s*["\'][a-zA-Z0-9-]{10,}["\']': "❌ Found potential Hardcoded Key",
    r'[ก-๙]': "❌ Found Thai characters/comments (Clean up chat logs)",
    r'sqlite3\.connect': "⚠️ Found SQLite usage (Critical for Enterprise check)"
}

IGNORE_FILES = ['audit_guard.py', '.env', 'requirements.txt', 'README.md']

def scan_project(directory="."):
    print(f"🛡️  CODEX GUARD: Scanning {os.path.abspath(directory)}...")
    issues_found = False

    for root, _, files in os.walk(directory):
        if "venv" in root or ".git" in root or "__pycache__" in root:
            continue

        for file in files:
            if not file.endswith(".py") or file in IGNORE_FILES:
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.readlines()
                    
                for i, line in enumerate(content):
                    for pattern, message in FORBIDDEN_PATTERNS.items():
                        if re.search(pattern, line):
                            print(f"\n📂 File: {filepath}")
                            print(f"   Line {i+1}: {line.strip()}")
                            print(f"   🚨 {message}")
                            issues_found = True
            except Exception as e:
                print(f"⚠️ Could not read {file}: {e}")

    print("-" * 50)
    if issues_found:
        print("🛑 AUDIT FAILED: Do NOT push to GitHub yet!")
        sys.exit(1)
    else:
        print("✅ AUDIT PASSED: Code is clean. You may proceed to push.")
        sys.exit(0)

if __name__ == "__main__":
    scan_project()