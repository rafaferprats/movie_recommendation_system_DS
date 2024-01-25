from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"greetings": "welcome"}


#def test_movie_recommendation_via_user():
#    response = client.get("/movie_recommendation_via_user/1")
#    assert response.status_code == 200
#    from main import get_movie_from_user
#    assert response.json() == get_movie_from_user(1).to_json()

#def test_movie_recommendation_via_movie():
#    response = client.get("/movie_recommendation_via_movie/4162")
#    assert response.status_code == 200
#    from main import get_movie_from_movie
#    assert response.json() == get_movie_from_movie(4162).to_json()


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
    response_1 = client.get("/add_user/movieid/128715/rating/5")
    assert response_1.status_code == 200
    assert response_1.json() == {
  "new userId as": 1032,
  "movieId": 128715,
  "movie title": "Eloise at the Plaza (2003)",
  "rating score": 5,
  "the user has been": "added to our DB"
}
#add rating to existing user, existing movie
    # movie exits
    response_2 = client.get("/userid/1/movieid/128715/rating/5")
    assert response_2.status_code == 200
    assert response_2.json() == {
  "userId as": 1,
  "movieId": 128715,
  "movie title": "Eloise at the Plaza (2003)",
  "rating score": 5,
  "the movie has been rated": "and added to our DB"
}
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
def test_show_db_data():
    response_1 = client.get("/show_db_data/")
    assert response_1.status_code == 200
    assert response_1.json() == {
  "The numbers of users in db are: ": 1032,
  "The numbers of movies in db are: ": 9648,
  '-> List rating of the movies from 0.5 to 5': '',
  "rating of the movies with 0.5": 2743,
  "rating of the movies with 1": 5741,
  "rating of the movies with 1.5": 2106,
  "rating of the movies with 2": 11005,
  "rating of the movies with 2.5": 5914,
  "rating of the movies with 3": 31741,
  "rating of the movies with 3.5": 14643,
  "rating of the movies with 4": 39416,
  "rating of the movies with 4.5": 11118,
  "rating of the movies with 5": 20686
}

#show score
def test_show_score():
    response_1 = client.get("/show_scores/")
    assert response_1.status_code == 200
    assert response_1.json() == {
  "Labels: ": [
    "num_retraining",
    "retraining_time_seconds",
    "num_users",
    "db_score_reco_user_15",
    "db_score_reco_user_25",
    "db_score_reco_user_35",
    "db_score_reco_user_45",
    "db_score_reco_movie_15",
    "db_score_reco_movie_25",
    "db_score_reco_movie_35",
    "db_score_reco_movie_45",
    "ch_score_reco_user_15",
    "ch_score_reco_user_25",
    "ch_score_reco_user_35",
    "ch_score_reco_user_45",
    "ch_score_reco_movie_15",
    "ch_score_reco_movie_25",
    "ch_score_reco_movie_35",
    "ch_score_reco_movie_45"
  ],
  "Values: ": [
    6,
    71,
    1031,
    0.48,
    0.46,
    0.49,
    0.48,
    0.49,
    0.47,
    0.49,
    0.49,
    4800151.91,
    8367100.72,
    11554208.82,
    15101824.06,
    2387675.03,
    4419628.8,
    6024810.7,
    7596943.3
  ]
}

#delete users
def test_delete_user():
    response_1 = client.get("/delete_user/1032")
    assert response_1.status_code == 200
    assert response_1.json() == [
  "We dont have that user in our DB, try another one"
]
    response_2 = client.get("/delete_user/100")
    assert response_1.status_code == 200
    assert response_1.json() == {
  "userId as": 100,
  "The user has been removed from our DB ": " "
}

#delete movies
def test_delete_user():
    response_1 = client.get("/delete_movie/2478")
    assert response_1.status_code == 200
    assert response_1.json() == {
      "movieId as": 2478,
      "The movie with the following title has been removed from our DB -> ": "¡Three Amigos! (1986)"
    }
