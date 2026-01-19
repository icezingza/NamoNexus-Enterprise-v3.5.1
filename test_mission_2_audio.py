import requests
import wave
import struct
import os
import sys
import json

# ตั้งค่าการแสดงผลภาษาไทยใน Windows Terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# --- Config ---
API_URL = "http://127.0.0.1:8000/triage/audio"
TEST_FILE = "synthetic_voice_test.wav"
# Retrieve token from env or use default for local dev
TOKEN = os.getenv("NAMO_NEXUS_TOKEN", "DwTuv-cSiI2XwdQ4FoaNih5qGUUbru_yrD3-IvJKUw8=")

def create_dummy_wav(filename):
    """สร้างไฟล์เสียง WAV จำลอง (Silence/Noise) เพื่อใช้ทดสอบการอัปโหลด"""
    print(f"🔊 Generating dummy audio file: {filename}...")
    with wave.open(filename, 'w') as wav_file:
        # Set parameters: 1 channel, 2 byte width, 44100 sampling rate, n frames
        wav_file.setparams((1, 2, 44100, 44100, 'NONE', 'not compressed'))
        # Generate some dummy data (silence/noise)
        for _ in range(44100):
            value = struct.pack('h', 0) # Silence
            wav_file.writeframes(value)
    print("✅ Dummy audio created.")

def run_mission_2():
    print("\n🎧 --- MISSION 2: AUDIO TRIAGE INITIATED ---")
    
    # 1. สร้างไฟล์เสียงถ้ายังไม่มี
    if not os.path.exists(TEST_FILE):
        create_dummy_wav(TEST_FILE)

    # 2. ยิงไฟล์เข้า API
    try:
        print(f"🚀 Sending {TEST_FILE} to {API_URL}...")
        headers = {"Authorization": f"Bearer {TOKEN}"}
        with open(TEST_FILE, 'rb') as f:
            # Note: API expects 'audio_file' or 'audio'
            files = {'audio_file': (TEST_FILE, f, 'audio/wav')}
            data = {'user_id': 'mission_2_agent'}
            
            response = requests.post(API_URL, files=files, data=data, headers=headers)
            
            # 3. ตรวจสอบผลลัพธ์
            if response.status_code == 200:
                res = response.json()
                print("\n📊 --- API RESPONSE RECEIVED ---")
                print(json.dumps(res, indent=2, ensure_ascii=False))
                
                # 4. Victory Check
                print("\n🏆 --- VICTORY KEYS VERIFICATION ---")
                
                # Check 1: Risk Level
                risk = res.get('risk_level')
                if risk:
                    print(f"[Risk Level]: {risk} -> ✅ PASSED")
                else:
                    print(f"[Risk Level]: NOT FOUND -> ❌ FAILED")

                # Check 2: Golden Ratio (Voice vs Text)
                voice_score = res.get('voice_score', 'N/A (Internal)')
                text_score = res.get('text_score', 'N/A (Internal)')
                
                print(f"[Voice Score]: {voice_score}")
                print(f"[Text Score]: {text_score}")
                
                if 'multimodal_confidence' in res:
                     print(f"[Confidence]: {res['multimodal_confidence']} -> ✅ PASSED")
                     print("\n🎉 MISSION 2: PASSED! Seraphina has ears.")
                else:
                     print("\n⚠️ MISSION 2: PARTIAL PASS (Confidence missing)")
                
            else:
                print(f"\n❌ FAILED: API Error {response.status_code}")
                print(response.text)
                
    except Exception as e:
        print(f"\n❌ SYSTEM ERROR: {e}")
        print("💡 Hint: ตรวจสอบว่า Server (uvicorn) ยังรันอยู่ไหม?")
    
    finally:
        # Clean up
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)
            print(f"\n🧹 Cleaned up {TEST_FILE}")

if __name__ == "__main__":
    run_mission_2()