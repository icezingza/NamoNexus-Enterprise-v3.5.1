import os
import sys
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict

def check_dependencies():
    print("🔍 [Step 1] Checking Dependencies...")
    requirements_path = 'requirements.txt'
    
    if not os.path.exists(requirements_path):
        print(f"❌ Error: {requirements_path} not found!")
        return False

    with open(requirements_path, 'r') as f:
        # Filter out comments and empty lines, and handle environment markers simply
        requirements = [
            line.strip().split(';')[0] 
            for line in f 
            if line.strip() and not line.startswith('#')
        ]

    try:
        pkg_resources.require(requirements)
        print("✅ All dependencies are installed.")
        return True
    except (DistributionNotFound, VersionConflict) as e:
        print(f"❌ Dependency Issue: {e}")
        print("👉 Please run: pip install -r requirements.txt")
        return False

def check_identity_capsule():
    print("\n🔍 [Step 2] Checking Identity Capsule...")
    identity_path = os.path.join('core', 'identity')
    
    if not os.path.exists(identity_path):
        print(f"❌ Error: Directory '{identity_path}' not found.")
        print("👉 Please ensure the 'core/identity' folder exists.")
        return False
    
    files = os.listdir(identity_path)
    if not files:
        print(f"⚠️  Warning: '{identity_path}' is empty.")
        return False
        
    print(f"✅ Identity Capsule found ({len(files)} files).")
    return True

if __name__ == "__main__":
    print("=== NamoNexus Readiness Check ===\n")
    deps_ok = check_dependencies()
    capsule_ok = check_identity_capsule()
    
    if deps_ok and capsule_ok:
        print("\n🚀 System Ready for Ignition!")
    else:
        print("\n🛑 Please fix the issues above before starting.")