import os
import shutil
import glob

def reorganize():
    """
    Reorganizes the project structure based on the Audit Report v3.5.1.
    Moves loose files from Root into categorized subdirectories.
    """
    base_dir = os.getcwd()
    
    # Define the target structure: { "Destination Folder": ["File Patterns"] }
    structure = {
        "core": ["voice_extractor.py"],
        "api": ["main.py"],
        "tests": ["test_mission_*.py", "verify_setup*.py"],
        "scripts": ["*.bat", "*.ps1", "*.sh"],
        "frontend": ["index.html", "*.css", "*.js"],
        "data": ["*.db", "*.sqlite", "*.sqlite3"],
    }
    
    # Files to explicitly exclude from moving
    exclude = [
        "reorganize_structure.py", 
        "requirements.txt", 
        "README.md", 
        "Dockerfile", 
        "LICENSE", 
        ".env", 
        ".gitignore"
    ]

    print(f"📦 Starting NamoNexus Reorganization in: {base_dir}")

    for folder, patterns in structure.items():
        target_dir = os.path.join(base_dir, folder)
        
        # 1. Create directory if missing
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"  ➕ Created directory: {folder}/")
            
        # 2. Find and move files
        for pattern in patterns:
            # Search for files in the root directory only
            files = glob.glob(os.path.join(base_dir, pattern))
            
            for file_path in files:
                filename = os.path.basename(file_path)
                
                if filename in exclude or os.path.isdir(file_path):
                    continue

                dest_path = os.path.join(target_dir, filename)
                
                # Avoid moving if already in place (though glob(root) shouldn't see inside folders)
                if os.path.dirname(file_path) == base_dir:
                    try:
                        shutil.move(file_path, dest_path)
                        print(f"  ✅ Moved: {filename} -> {folder}/")
                    except Exception as e:
                        print(f"  ❌ Failed to move {filename}: {e}")

    print("\n🎉 Reorganization complete!")
    print("⚠️  IMPORTANT: Please update your import paths (e.g., 'from voice_extractor' -> 'from core.voice_extractor').")

if __name__ == "__main__":
    reorganize()