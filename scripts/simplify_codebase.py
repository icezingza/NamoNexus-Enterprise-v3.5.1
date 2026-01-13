import shutil
from pathlib import Path
import subprocess
import sys


def simplify_codebase():
    """Move non-essential modules to research folder"""

    # STEP 0: BACKUP (5 seconds)
    print("Creating backup...")
    try:
        subprocess.run(
            ["git", "tag", "-a", "backup-before-mvp", "-m", "MVP cleanup backup"],
            check=True,
        )
    except subprocess.CalledProcessError:
        print(
            "Warning: Tag 'backup-before-mvp' might already exist or git failed. Continuing..."
        )

    base = Path("app")
    research = Path("research")
    research.mkdir(exist_ok=True)

    # Your exact list
    archive_modules = [
        "civilization",
        "cloud",
        "continuum",
        "genesis",
        "governance",
        "hypercognitive",
        "transcendent",
        "universal",
        "network/quantum",
        "network/global",
    ]

    # Step 1: Archive (your approach)
    print("\n🧹 Archiving research modules...")
    for module in archive_modules:
        src = base / module
        if src.exists():
            dst = research / module
            dst.parent.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {src} -> {dst}")
            shutil.move(str(src), str(dst))
        else:
            print(f"  - {src} not found, skipping.")

    # Step 2: Delete unused
    print("\n🗑️  Deleting unused files...")
    for file in ["api/dashboard.py", "api/monitoring.py"]:
        f = base / file
        if f.exists():
            print(f"  ✓ {f}")
            f.unlink()
        else:
            print(f"  - {f} not found, skipping.")

    # STEP 3: VERIFY (my addition - 30 seconds)
    print("\n✅ Verifying...")
    try:
        # Assuming src.main is importable. Adjust path if needed.
        # Adding current dir to sys.path to ensure imports work
        sys.path.append(str(Path.cwd()))
        from src.main import app

        print("  ✓ Imports OK")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        print("  -> Rolling back...")
        subprocess.run(["git", "reset", "--hard", "backup-before-mvp"])
        return False

    print("\n✅ SIMPLIFICATION COMPLETE!")
    print("Next: git add -A && git commit -m '...'")
    return True


if __name__ == "__main__":
    success = simplify_codebase()
    exit(0 if success else 1)
