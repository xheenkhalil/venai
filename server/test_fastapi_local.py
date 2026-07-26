import httpx
from fastapi.testclient import TestClient
from app.main import app
import asyncio

async def test_endpoint():
    print("Starting client...")
    client = TestClient(app)
    
    print("Testing /api/v1/procurement-requests/ ...")
    try:
        response = client.get("/api/v1/procurement-requests/", headers={"Authorization": "Bearer whatever"})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception raised: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
