from app import app

def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "UP"

def test_hello():
    client = app.test_client()
    response = client.get("/api/v1/hello?name=Sample-API")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Sample-API"
