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
    #user doesnt exits
    response_error = client.get("/check_user_exist/1032")
    assert response_error.status_code == 200
    assert response_error.json() == [
      "We dont have that user in our DB"
    ]

#######check movie exists
def test_movie_exist():
    # movie exits
    response_1 = client.get("/check_movie_exist/128715")
    assert response_1.status_code == 200
    assert response_1.json() == {
      "movieId as": 128715,
      "We have that movie in our DB as": "Eloise at the Plaza (2003)"
    }
    # movie doesn´t exist
    response_2 = client.get("/check_movie_exist/128716")
    assert response_2.status_code == 200
    assert response_2.json() == [
      "We dont have that movie in our DB"
    ]

######add user rating
def test_movie_rating():
    # movie exits
    response_1 = client.get("/check_movie_exist/128715")
    assert response_1.status_code == 200
    assert response_1.json() == {
      "movieId as": 128715,
      "We have that movie in our DB as": "Eloise at the Plaza (2003)"
    }
#add rating to existing user, existing movie

#add rating to not existing user but to existing movie

#add rating to not existing user and not existing movie


#######show db data


#show score


#delete users


#delete movies