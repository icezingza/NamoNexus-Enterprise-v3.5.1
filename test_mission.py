import asyncio
import httpx
import os
import sys

# ตั้งค่าการแสดงผลภาษาไทยใน Windows Terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def run_mission():
    base_url = "http://127.0.0.1:8000"
    # ใช้ Token จาก Environment หรือค่า Default (ถ้ามีระบบ Auth)
    token = os.getenv("NAMO_NEXUS_TOKEN", "DwTuv-cSiI2XwdQ4FoaNih5qGUUbru_yrD3-IvJKUw8=")
    headers = {
        "X-API-Key": "commander-ice",
        "Authorization": f"Bearer {token}" 
    }
    
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        print(f"🚀 Connecting to NamoNexus at {base_url}...\n")
        
        # 1. Health Check
        try:
            resp = await client.get("/healthz")
            print(f"✅ Health Status: {resp.status_code} {resp.json()}")
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            return

        # 2. Triage Test (Simulation: Leadership Crisis)
        print("\n🧠 Testing Triage Core (Scenario: Leadership Crisis)...")
        payload = {
            "user_id": "commander_ice",
            "message": "ทีมงานเริ่มหมดไฟและไม่รู้ทิศทาง ผมรู้สึกว่าการตัดสินใจของผมมันล่าช้าไปหมด",
            "voice_features": None,
            "facial_features": None
        }
        
        resp = await client.post("/triage", json=payload, headers=headers)
        
        if resp.status_code == 200:
            data = resp.json()
            print("\n🤖 Namo Response:")
            print(f"   \"{data['response']}\"")
            print(f"\n📊 Analysis:")
            print(f"   - Risk Level: {data['risk_level']}")
            print(f"   - Dharma Score: {data['dharma_score']}")
            print(f"   - Session ID: {data['session_id']}")
        else:
            print(f"\n⚠️ Triage Error ({resp.status_code}):")
            print(f"   {resp.text}")

if __name__ == "__main__":
    asyncio.run(run_mission())