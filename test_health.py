from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_healthz_endpoint():
    """
    Unit Test สำหรับตรวจสอบ API /healthz
    ใช้สำหรับ Kubernetes Liveness/Readiness Probes
    """
    print("\n🩺 Testing /healthz endpoint...")
    response = client.get("/healthz")
    
    # ต้องได้ Status Code 200 OK เสมอ เพื่อบอกว่าระบบปกติ
    assert response.status_code == 200, f"❌ Health check failed! Expected 200 but got {response.status_code}"
    print("✅ /healthz is healthy (200 OK)")