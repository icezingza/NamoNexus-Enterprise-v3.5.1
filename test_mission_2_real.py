import requests
import os
import json
import glob
import sys

# ตั้งค่าการแสดงผลภาษาไทยใน Windows Terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# --- Config ---
# พิกัดคลังแสงของพี่ไอซ์
AUDIO_DIR = r"D:\Users\NamoNexus Enterprise v3.5.1\Audio test"
API_URL = "http://127.0.0.1:8000/triage/audio"

def run_mission_2_real():
    print(f"\n🎧 --- MISSION 2: REAL AUDIO TEST INITIATED ---")
    print(f"📂 Searching in: {AUDIO_DIR}")

    # 1. ค้นหาไฟล์เสียงในโฟลเดอร์ (เอาไฟล์ไหนก็ได้ที่เป็น .mp3 หรือ .wav)
    audio_files = glob.glob(os.path.join(AUDIO_DIR, "*.mp3")) + glob.glob(os.path.join(AUDIO_DIR, "*.wav"))
    
    if not audio_files:
        print(f"❌ ไม่เจอไฟล์เสียงในโฟลเดอร์ครับ! พี่ช่วยเช็คหน่อยว่ามีไฟล์ .mp3/.wav ในนั้นไหม?")
        return

    # เลือกไฟล์แรกที่เจอมาเทสเลย
    target_file = audio_files[0]
    print(f"🎯 Target Acquired: {os.path.basename(target_file)}")

    # 2. ยิงไฟล์เข้า API
    try:
        print(f"🚀 Sending payload...")
        with open(target_file, 'rb') as f:
            # เดา Content-Type ง่ายๆ
            mime_type = 'audio/mpeg' if target_file.endswith('.mp3') else 'audio/wav'
            
            # แก้ไขชื่อ field จาก 'file' เป็น 'audio_file' ให้ตรงกับ main.py
            files = {'audio_file': (os.path.basename(target_file), f, mime_type)}
            data = {'user_id': 'mission_2_agent'}
            
            # เพิ่ม Token ถ้าจำเป็น (ใช้ค่า Default ถ้าไม่มีใน Env)
            token = os.getenv("NAMO_NEXUS_TOKEN", "DwTuv-cSiI2XwdQ4FoaNih5qGUUbru_yrD3-IvJKUw8=")
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.post(API_URL, files=files, data=data, headers=headers)
            
            # 3. ตรวจสอบผลลัพธ์
            if response.status_code == 200:
                res = response.json()
                print("\n📊 --- API RESPONSE RECEIVED ---")
                # print(json.dumps(res, indent=2, ensure_ascii=False)) # ปิดไว้จะได้ไม่รก
                
                print("\n🏆 --- VICTORY KEYS VERIFICATION ---")
                print(f"[Risk Level]: {res.get('risk_level', 'N/A')}")
                
                # ดึงค่าจาก voice_features dict ถ้ามี
                voice_features = res.get('voice_features', {})
                if isinstance(voice_features, dict):
                    print(f"[Voice Energy]: {voice_features.get('energy', 0):.2f}")
                    print(f"[Pitch Variance]: {voice_features.get('pitch_variance', 0):.2f}")
                
                print(f"[Transcription]: {res.get('transcription', 'N/A')}")
                
                if 'multimodal_confidence' in res:
                     print(f"[Confidence]: {res['multimodal_confidence']} -> ✅ PASSED")
                     print("\n🎉 MISSION 2 COMPLETE: Seraphina heard the truth!")
                else:
                     print("\n⚠️ PARTIAL SUCCESS: Data received but confidence missing.")
                
            else:
                print(f"\n❌ FAILED: API Error {response.status_code}")
                print(f"Server Says: {response.text}")
                print("💡 Hint: ถ้ายัง 500 แปลว่าอาจขาด FFmpeg หรือ Code ใน Server (backend) มีบั๊ก")
                
    except Exception as e:
        print(f"\n❌ SYSTEM ERROR: {e}")

if __name__ == "__main__":
    run_mission_2_real()