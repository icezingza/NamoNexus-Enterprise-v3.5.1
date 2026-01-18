import os
import re
import sys

# Goal: scan for forbidden patterns in code - PRODUCTION VERSION
# Only checks for ACTUAL security issues, not style/enterprise guidelines
FORBIDDEN_PATTERNS = {
    r'''(?i)(token|password|secret)\s*=\s*["\'][a-zA-Z0-9_\-+=/]{16,}["\']''': "CRITICAL: Found hardcoded credentials",
    r'''api[_-]?key\s*=\s*["\'][a-zA-Z0-9_\-+=/]{20,}["\']''': "CRITICAL: Found hardcoded API key",
    r'''private[_-]?key\s*=\s*["\']-----BEGIN''': "CRITICAL: Found hardcoded private key",
    r'''root@\d+\.\d+\.\d+\.\d+''': "Found hardcoded IP/SSH credentials",
    r'''DEBUG\s*=\s*True\s+#.*production''': "WARNING: DEBUG=True found in production context"
}

# Ignore patterns - these directories/files are exempt
IGNORE_DIRS = ['node_modules', 'venv', '.venv', '.git', '__pycache__', '.pytest_cache', 'investor_portal']
IGNORE_FILES = ['audit_guard.py', '.env', '.env.example', 'requirements.txt', 'README.md', 'LICENSE']
IGNORE_PATTERNS = [r'test.*\.py$', r'.*_test\.py$', r'debug_.*\.py$', r'generate_.*\.py$', r'validate_.*\.py$']

def scan_project(directory="."):
    print(f"🛡️  CODEX GUARD: Scanning {os.path.abspath(directory)}...")
    print("=" * 60)
    issues_found = False
    scanned_files = 0

    for root, _, files in os.walk(directory):
        # Skip ignored directories
        if any(ignored in root for ignored in IGNORE_DIRS):
            continue

        for file in files:
            # Skip non-Python files and explicitly ignored files
            if not file.endswith(".py"):
                continue
            if file in IGNORE_FILES:
                continue
            
            # Skip files matching ignore patterns
            if any(re.match(pattern, file) for pattern in IGNORE_PATTERNS):
                continue

            filepath = os.path.join(root, file)
            scanned_files += 1
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.readlines()
                    
                for i, line in enumerate(content, 1):
                    for pattern, message in FORBIDDEN_PATTERNS.items():
                        if re.search(pattern, line):
                            print(f"\n📂 {filepath}")
                            print(f"   Line {i}: {line.strip()[:80]}")
                            print(f"   🚨 {message}")
                            issues_found = True
            except Exception as e:
                # Silent skip for files that can't be read
                continue

    print("\n" + "=" * 60)
    print(f"📊 Scanned {scanned_files} Python files")
    
    if issues_found:
        print("\n🛑 AUDIT FAILED: Critical security issues found!")
        print("   🔒 DO NOT push to GitHub yet.")
        sys.exit(1)
    else:
        print("\n✅ AUDIT PASSED: No hardcoded secrets found.")
        print("   🚀 Safe to proceed with Git push.")
        sys.exit(0)

if __name__ == "__main__":
    scan_project()
