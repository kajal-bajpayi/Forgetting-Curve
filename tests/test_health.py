from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status":"ok"}

def test_openapi_documentation() -> None:
    response = client.get("/openapi.json")
    
    assert response.status_code == 200
    assert response.json()["info"]["title"] == 'Forgetting Curve API'

    