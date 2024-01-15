from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def testing():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"greetings": "welcome"}