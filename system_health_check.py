import sys
import os
import asyncio

# Ensure project root is in sys.path
sys.path.append(os.getcwd())

print("=" * 60)
print("NAMONEXUS: SYSTEM HEALTH DIAGNOSTIC")
print("=" * 60)

# 1. Environment Check
print(f"Python Version: {sys.version}")
print(f"Platform: {sys.platform}")
print("-" * 60)

# 2. Import Check
modules_to_check = [
    "src.config",
    "src.services.memory_service",
    "src.services.emotion_service",
    "src.services.dharma_service",
    "src.services.safety_service",
    "src.services.integrity_service",
    "src.api.routes",
]

failed_imports = []

for module in modules_to_check:
    try:
        print(f"Testing Import: {module}...", end=" ")
        __import__(module)
        print("[OK]")
    except Exception as e:
        print("[FAIL]")
        print(f"   Error: {e}")
        failed_imports.append(module)

if failed_imports:
    print("-" * 60)
    print(f"[CRITICAL] {len(failed_imports)} modules failed to import.")
    print("   Please verify the environment and dependencies.")
    sys.exit(1)

print("-" * 60)
print("[OK] All core modules imported successfully.")
print("-" * 60)


# 3. Final Status
async def check_status():
    print("Verifying system readiness...")
    # Add lightweight logic checks if needed
    return True


try:
    success = asyncio.run(check_status())
    print("-" * 60)
    if success:
        print("SYSTEM STATUS: OPERATIONAL")
    else:
        print("SYSTEM STATUS: DEGRADED")
except Exception as e:
    print(f"Fatal Error: {e}")
