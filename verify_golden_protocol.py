import os

# Color definitions for output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def check_file(path, required_keywords):
    """Verify file existence and presence of required logic components."""
    if not os.path.exists(path):
        return False, "File Missing ❌"

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            missing = [k for k in required_keywords if k not in content]
            if missing:
                return False, f"Missing Code: {missing} ⚠️"
            return True, "OK ✅"
    except Exception as e:
        return False, f"Error: {e}"


# Core system integrity checklist
checklist = {
    "src/config.py": ["class Config", "API_HOST"],
    "src/services/memory_service.py": ["class MemoryService", "store_experience"],
    "src/services/emotion_service.py": ["class EmotionService", "analyze_sentiment"],
    "src/services/dharma_service.py": [
        "class DharmaAlignmentService",
        "apply_four_noble_truths",
    ],
    "src/services/safety_service.py": [
        "class SafetyService",
        "detect_critical_anomaly",
    ],
    "src/services/integrity_service.py": ["class IntegrityKernel", "validate_action"],
    "src/api/routes.py": ['@router.post("/interact")', "handle_interaction"],
}

print("\n" + "=" * 60)
print("🔍  NAMONEXUS: SYSTEM INTEGRITY AUDIT")
print("=" * 60)

score = 0
total = len(checklist)

for file_path, keywords in checklist.items():
    passed, status = check_file(file_path, keywords)
    if passed:
        print(f"{GREEN}[PASS]{RESET} {file_path:<45} {status}")
        score += 1
    else:
        print(f"{RED}[FAIL]{RESET} {file_path:<45} {status}")

print("-" * 60)
if score >= total:
    print(f"{GREEN}✨ SYSTEM STATUS: OPERATIONAL ✨{RESET}")
    print("   All core components verified.")
else:
    print(f"{RED}⚠️ SYSTEM STATUS: INCOMPLETE{RESET}")
    print(f"   Score: {score}/{total}")
print("=" * 60 + "\n")
