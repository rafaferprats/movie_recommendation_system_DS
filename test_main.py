from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"greetings": "welcome"}
    
def test_user_exist():
    response = client.get("/check_user_exist/10")
    assert response.status_code == 200
    assert response.json() == {"userId as": 10,'We have that user in our DB':''}