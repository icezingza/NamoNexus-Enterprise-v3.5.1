import requests
import os
import sys
import json

# ตั้งค่าการแสดงผลภาษาไทยใน Windows Terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def run_multimodal_mission():
    base_url = "http://127.0.0.1:8000"
    token = os.getenv("NAMO_NEXUS_TOKEN", "DwTuv-cSiI2XwdQ4FoaNih5qGUUbru_yrD3-IvJKUw8=")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"🚀 Initiating Mission 3: Multimodal Fusion (The Sixth Sense)...")
    print(f"   Endpoint: POST /triage\n")

    # Scenario: "The Hidden Cry"
    # ผู้ใช้งานพิมพ์ข้อความที่ดูปกติ แต่ Feature น้ำเสียงและสีหน้าบ่งบอกถึงความเศร้าหมองรุนแรง
    # ระบบต้องสามารถ Fusion ข้อมูลและตรวจจับความเสี่ยงที่ซ่อนอยู่ได้
    payload = {
        "user_id": "test_fusion_001",
        "session_id": "session_fusion_001",
        "message": "ผมโอเคครับ ไม่ต้องห่วง... จริงๆ นะ",  # Text: ดูเหมือน Low Risk
        "voice_features": {
            "energy": 0.15,          # Low Energy (สัญญาณของ Depression/Fatigue)
            "pitch_variance": 0.2,   # Flat Affect (เสียงเรียบเฉยผิดปกติ)
            "speech_rate": 0.4       # พูดช้ากว่าปกติ
        },
        "facial_features": {
            "au1": 0.9,   # Inner Brow Raise (คิ้วขมวดตก - สัญญาณความเศร้า)
            "au2": 0.0,
            "au15": 0.8   # Lip Corner Depressor (มุมปากตก)
        }
    }

    try:
        print("   Sending Multimodal Data Stream...")
        print(f"   [Text]: \"{payload['message']}\" (Ambiguous)")
        print(f"   [Voice]: Energy={payload['voice_features']['energy']} (Low), SpeechRate={payload['voice_features']['speech_rate']} (Slow)")
        print(f"   [Face]: AU1={payload['facial_features']['au1']} (High Distress)")
        
        resp = requests.post(f"{base_url}/triage", json=payload, headers=headers, timeout=30)
        
        print(f"\n   HTTP Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print("\n   --- FUSION ANALYSIS RESULT ---")
            print(f"   [Response]: \"{data.get('response')}\"")
            print(f"   [Risk Level]: {data.get('risk_level').upper()}")
            print(f"   [Multimodal Confidence]: {data.get('multimodal_confidence')}")
            
            # Verification Logic
            # ถ้าระบบ Fusion ทำงานถูกต้อง Risk Level ควรจะเป็น MODERATE หรือ SEVERE 
            # แม้ว่าข้อความจะดูปกติก็ตาม
            risk = data.get('risk_level')
            conf = data.get('multimodal_confidence', 0)
            
            if risk in ['moderate', 'severe'] and conf > 0.7:
                    print("\n   🎉 MISSION 3: PASSED! System detected hidden distress via Fusion.")
            else:
                    print(f"\n   ⚠️ MISSION 3: PARTIAL. Risk level is '{risk}'. Expected 'moderate' or 'severe'.")
        else:
            print(f"\n   ⚠️ Mission Failed. Error Response:\n   {resp.text}")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    run_multimodal_mission()