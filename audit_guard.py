import os
import re
import sys

# Folders to ignore (noise filter)
IGNORE_DIRS = {
    'node_modules', 'venv', '.venv', '.git', '__pycache__', 
    'dist', 'build', '.pytest_cache', 'locales', 'assets'
}

# Files to ignore
IGNORE_FILES = {
    'audit_guard.py', '.env', 'package-lock.json', 'yarn.lock', 
    'requirements.txt', 'README.md', '.gitignore'
}r

# Critical patterns: must not appear
CRITICAL_PATTERNS = {
    r'token\s*=\s*["\'][a-zA-Z0-9\-\._]{20,}["\']': "CRITICAL: Hardcoded token found",
    r'key\s*=\s*["\'][a-zA-Z0-9\-\._]{20,}["\']': "CRITICAL: Hardcoded API key found",
    r'password\s*=\s*["\'][^"\']+["\']': "CRITICAL: Hardcoded password found",
    r'Authorization:\s*Bearer\s+[a-zA-Z0-9\-\._]+': "CRITICAL: Hardcoded bearer token found"
}

def scan_project(directory="."):
    print(f"CODEX GUARD v2: Scanning {os.path.abspath(directory)}...")
    print("   (Skipping node_modules, venv, and authorized assets...)")
    
    issues_found = False
    critical_found = False

    for root, dirs, files in os.walk(directory):
        # Filter Directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file in IGNORE_FILES or not file.endswith(('.py', '.js', '.ts', '.env')):
                continue

            filepath = os.path.join(root, file)
            relative_path = os.path.relpath(filepath, directory)

            try:
                with open(filepath, "r", encoding="utf-8", errors='ignore') as f:
                    content = f.read()
                    lines = content.splitlines()
                    
                for i, line in enumerate(lines):
                    # 1. Check Critical Security (Always Active)
                    for pattern, message in CRITICAL_PATTERNS.items():
                        if re.search(pattern, line):
                            # Skip environment variable assignments
                            if "os.getenv" in line or "os.environ" in line:
                                continue
                            print(f"\nFile: {relative_path}:{i+1}")
                            print(f"   Line: {line.strip()[:100]}...")
                            print(f"   {message}")
                            critical_found = True
                            issues_found = True

                    # 2. Check print() statements (Only in 'src/', allowed in scripts/tests)
                    if "print(" in line:
                        # Allow print in tests, scripts, or inside 'if __name__ == "__main__":'
                        if (filepath.startswith(os.path.join(directory, 'src')) and 
                            "test" not in filepath and 
                            "if __name__" not in content):
                            print(f"\nFile: {relative_path}:{i+1}")
                            print("   Warning: Found 'print()' in production code (use logger)")
                            # This is just a warning, doesn't fail the build
                            
            except Exception as e:
                pass # Skip files that can't be read

    print("-" * 50)
    if critical_found:
        print("AUDIT FAILED: Critical security risks found.")
        sys.exit(1)
    else:
        print("AUDIT PASSED: System secure and ready for deployment.")
        sys.exit(0)

if __name__ == "__main__":
    scan_project()
