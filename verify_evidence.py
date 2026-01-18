import sys
import os


def verify_log(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # ตรวจสอบ HTTP Status Code (ต้องใช้ curl -i ถึงจะมี Header นี้)
    if "HTTP/1.1 200" in content or "HTTP/2 200" in content:
        print(f"✅ {file_path}: Verified HTTP 200 OK")
        return True
    else:
        print(f"❌ {file_path}: HTTP 200 OK NOT found in headers.")
        return False


if __name__ == "__main__":
    # รายชื่อไฟล์ Log ที่ต้องการตรวจสอบ
    files_to_check = ["health.log", "triage_audio.log", "triage.log"]
    success = True

    for log_file in files_to_check:
        if not verify_log(log_file):
            success = False

    if not success:
        sys.exit(1)
    print("🎉 All evidence logs verified successfully!")
