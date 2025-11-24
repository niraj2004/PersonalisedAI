from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    print("Testing /health endpoint...")
    response = client.get("/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["db"] == "connected"
    print("✅ /health check passed")

if __name__ == "__main__":
    test_health_check()
