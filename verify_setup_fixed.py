import os
import sys
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict

def check_dependencies():
    print("[i] [Step 1] Checking Dependencies...")
    requirements_path = 'requirements.txt'
    
    if not os.path.exists(requirements_path):
        print(f"[X] Error: {requirements_path} not found!")
        return False

    filtered_requirements = []
    
    with open(requirements_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            # Split on ';' to separate requirement from environment marker
            if ';' in line:
                requirement_part, marker_part = line.split(';', 1)
                requirement_part = requirement_part.strip()
                marker_part = marker_part.strip()
                
                # Evaluate the marker against current platform
                try:
                    if pkg_resources.evaluate_marker(marker_part):
                        # Marker matches current platform, include this requirement
                        filtered_requirements.append(requirement_part)
                    else:
                        # Marker doesn't match, skip this requirement
                        print(f"[i] Skipping '{requirement_part}' (does not match current platform)")
                except Exception as e:
                    print(f"[!] Warning: Could not evaluate marker '{marker_part}' on line {line_num}: {e}")
                    # If we can't evaluate the marker, be conservative and include the requirement
                    filtered_requirements.append(requirement_part)
            else:
                # No environment marker, include the requirement
                filtered_requirements.append(line)

    if not filtered_requirements:
        print("[!] Warning: No requirements to check after filtering.")
        return True

    try:
        pkg_resources.require(filtered_requirements)
        print("[OK] All platform-appropriate dependencies are installed.")
        return True
    except DistributionNotFound as e:
        print(f"[X] Missing Dependency: {e}")
        print("[TIP] Please run: pip install -r requirements.txt")
        return False
    except VersionConflict as e:
        print(f"[X] Version Conflict: {e}")
        print("[TIP] Please run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"[X] Unexpected error checking dependencies: {e}")
        return False

def check_identity_capsule():
    print("\n[i] [Step 2] Checking Identity Capsule...")
    identity_path = os.path.join('core', 'identity')
    
    if not os.path.exists(identity_path):
        print(f"[X] Error: Directory '{identity_path}' not found.")
        print("[TIP] Please ensure the 'core/identity' folder exists.")
        return False
    
    files = os.listdir(identity_path)
    if not files:
        print(f"[!] Warning: '{identity_path}' is empty.")
        return False
        
    print(f"[OK] Identity Capsule found ({len(files)} files).")
    return True

def check_tests_structure():
    print("\n[i] [Step 3] Checking Test Suite...")
    tests_path = 'tests'
    health_test_path = os.path.join(tests_path, 'test_health.py')
    
    if not os.path.exists(tests_path):
        print(f"[X] Error: Directory '{tests_path}' not found.")
        return False
    
    if not os.path.exists(health_test_path):
        print(f"[X] Error: File '{health_test_path}' not found.")
        return False
        
    print(f"[OK] Test Suite found ('{tests_path}' directory and health check).")
    return True

if __name__ == "__main__":
    print("=== NamoNexus Readiness Check ===\n")
    deps_ok = check_dependencies()
    capsule_ok = check_identity_capsule()
    tests_ok = check_tests_structure()
    
    if deps_ok and capsule_ok and tests_ok:
        print("\n[READY] System Ready for Ignition!")
    else:
        print("\n[STOP] Please fix the issues above before starting.")
