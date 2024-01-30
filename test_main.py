from fastapi.testclient import TestClient
import pandas as pd
from main import app
import pytest
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi import Depends

n_retrain = 0
final_db = pd.read_csv("data/final_db.csv")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
      yield c

@pytest.fixture(scope="module")
def test_user():
    return {"username": 2, "password": "2"}

def test_login(client, test_user):
    response = client.post("/token", data=test_user)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None
    return token

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"greetings": "welcome"}


def test_movie_recommendation_via_user(client, test_user):
    token = test_login(client, test_user)
    response = client.post("/movie_recomendation_via_movie/2", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    from main import get_movie_from_user
    assert isinstance(response.json(), dict)



def test_movie_recommendation_via_movie(client):
    response = client.get("/movie_recomendation_via_movie/4162")
    assert response.status_code == 200
    from main import get_movie_from_movie
    assert isinstance(response.json(), dict)


def test_user_exist(client):
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
def test_movie_exist(client):
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
def test_movie_rating(client):
    # movie exits
    response_1 = client.get("/add_user/movieid/128715/rating/5")
    assert response_1.status_code == 200
    assert isinstance(response_1.json(), dict)

#add rating to existing user, existing movie
    # movie exits
    response_2 = client.get("/userid/1/movieid/128715/rating/5")
    assert response_2.status_code == 200
    assert isinstance(response_2.json(), dict)

#add rating to not existing user but to existing movie
    response_3 = client.get("/userid/1033/movieid/128715/rating/5")
    assert response_3.status_code == 200
    assert response_3.json() == [
  "We dont have that movie added or that user, please check other endpoint to check the userid or movieid"
]
#add rating to not existing user and not existing movie
    response_4 = client.get("/userid/1/movieid/180000/rating/5")
    assert response_4.status_code == 200
    assert response_4.json() == [
  "We dont have that movie added or that user, please check other endpoint to check the userid or movieid"
]


#######show db data
def test_show_db_data(client: TestClient):
    global final_db
    rating_count_df = pd.DataFrame(final_db.groupby(['rating']).size(), columns=['count'])
    num_users = final_db['userId'].nunique()
    num_items = final_db['title'].nunique()

    response_1 = client.get("/show_db_data/")
    assert response_1.status_code == 200
    assert response_1.json() == {'The numbers of users in db are: ': int(num_users)+1,
            'The numbers of movies in db are: ': num_items,
            '-> List rating of the movies from 0.5 to 5':'',
            'rating of the movies with 0.5': int(rating_count_df['count'].iloc[0]),
            'rating of the movies with 1': int(rating_count_df['count'].iloc[1]),
            'rating of the movies with 1.5': int(rating_count_df['count'].iloc[2]),
            'rating of the movies with 2': int(rating_count_df['count'].iloc[3]),
            'rating of the movies with 2.5': int(rating_count_df['count'].iloc[4]),
            'rating of the movies with 3': int(rating_count_df['count'].iloc[5]),
            'rating of the movies with 3.5': int(rating_count_df['count'].iloc[6]),
            'rating of the movies with 4': int(rating_count_df['count'].iloc[7]),
            'rating of the movies with 4.5': int(rating_count_df['count'].iloc[8]),
            'rating of the movies with 5': int(rating_count_df['count'].iloc[9])+2,}

#show score
def test_show_score(client: TestClient):
    scores_data = pd.read_csv("data/movie_reco_scores.csv")
    sco_label = scores_data.columns.tolist()
    sco_retrain = scores_data.iloc[0].tolist()

    response_1 = client.get("/show_scores/")
    assert response_1.status_code == 200

#delete users
def test_delete_user(client: TestClient):
    response_1 = client.get("/delete_user/10032")
    assert response_1.status_code == 200
    assert response_1.json() == [
  "We dont have that user in our DB, try another one"
]
    response_2 = client.get("/delete_user/100")
    assert response_2.status_code == 200
    assert response_2.json() == {'userId as': 100,
                'The user has been removed from our DB ':' ',
}

#delete movies
def test_delete_movie(client: TestClient):

    response_1 = client.get("/delete_movie/2478")
    assert response_1.status_code == 200
    assert response_1.json() == {
      "movieId as": 2478,
      "The movie with the following title has been removed from our DB -> ": "¡Three Amigos! (1986)"
    }
