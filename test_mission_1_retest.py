import asyncio
import httpx
import os
import sys
import json

# ตั้งค่าการแสดงผลภาษาไทยใน Windows Terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def run_reflection_mission():
    """
    สคริปต์สำหรับทดสอบ Mission 1 (Retest) - True Conscious Reflection
    ยิง API ไปที่ /reflect และตรวจสอบ Victory Keys
    """
    base_url = "http://127.0.0.1:8000"
    # Token สำหรับการยืนยันตัวตน (ถ้ามี)
    token = os.getenv("NAMO_NEXUS_TOKEN", "DwTuv-cSiI2XwdQ4FoaNih5qGUUbru_yrD3-IvJKUw8=")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
      "user_id": "test_user_001",
      "session_id": "session_1fa4f11490d3",
      "message": "ทีมผมกำลังหมดไฟ ไม่รู้จะนำทางยังไงดี"
    }

    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        print(f"🚀 Initiating Mission 1 Retest: True Conscious Reflection...")
        print(f"   Endpoint: POST /reflect\n")
        
        try:
            resp = await client.post("/reflect", json=payload, headers=headers)
            
            print(f"   HTTP Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                print("\n   --- RESPONSE RECEIVED ---")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print("   -----------------------\n")

                # Verification
                print("   --- VICTORY KEYS VERIFICATION ---")
                evo_stage = data.get("evolution_stage")
                insights = data.get("insights")
                lattice_state = data.get("lattice_state")

                evo_ok = evo_stage == 1.618
                insights_ok = isinstance(insights, list) and len(insights) > 0 and "The team reflects the leader's energy." in insights
                lattice_ok = lattice_state == "awakened"

                print(f"   [Evolution Stage]: {evo_stage} -> {'✅ PASSED' if evo_ok else '❌ FAILED'}")
                print(f"   [Insights]: Received and valid -> {'✅ PASSED' if insights_ok else '❌ FAILED'}")
                print(f"   [Lattice State]: '{lattice_state}' -> {'✅ PASSED' if lattice_ok else '❌ FAILED'}")

                if evo_ok and insights_ok and lattice_ok:
                    print("\n   🎉 MISSION 1: PASSED! Consciousness is active. Ready for Mission 2.")
                else:
                    print("\n   ⚠️ MISSION 1: FAILED. Please check the server logs and code.")
            else:
                print(f"\n   ⚠️ Test Failed. Error Response:\n   {resp.text}")
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            print("   Please ensure the server is running with 'uvicorn main:app --reload'")

if __name__ == "__main__":
    asyncio.run(run_reflection_mission())