import pandas as pd
import numpy as np
import pickle
from fastapi import FastAPI
from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer,OAuth2PasswordRequestForm
from collections import Counter
import uvicorn
from pydantic import BaseModel
import sqlite3
from typing_extensions import Annotated
import datetime

# load the data
from sqlalchemy import create_engine
engine = create_engine('sqlite:///../data/movie.db', echo=False)

# read data from DB
ratings_data = pd.read_sql_query("SELECT * FROM ratings", engine)
movies_data = pd.read_sql_query("SELECT * FROM movies", engine)

# Load the saved model
with open("../models/svd_model.pkl", 'rb') as file:
    svd = pickle.load(file)

# Now you can use the model
def generate_recommendation(model, user_id, ratings_df, movies_df, n_items):
    # Get a list of all movie IDs from dataset
    movie_ids = ratings_df["movieId"].unique()

    # Get a list of all movie IDs that have been watched by user
    movie_ids_user = ratings_df.loc[ratings_df["userId"] == user_id, "movieId"]
    # Get a list off all movie IDS that that have not been watched by user
    movie_ids_to_pred = np.setdiff1d(movie_ids, movie_ids_user)

    # Apply a rating of 4 to all interactions (only to match the Surprise dataset format)
    test_set = [[user_id, movie_id, 4] for movie_id in movie_ids_to_pred]

    # Predict the ratings and generate recommendations
    predictions = model.test(test_set)
    pred_ratings = np.array([pred.est for pred in predictions])
    print("Top {0} item recommendations for user {1}:".format(n_items, user_id))
    # Rank top-n movies based on the predicted ratings
    index_max = (-pred_ratings).argsort()[:n_items]
    reco_list = []
    for i in index_max:
        movie_id = movie_ids_to_pred[i]
        reco_list.append((movies_df[movies_df["movieId"] == movie_id]["title"].values[0], pred_ratings[i]))
    return reco_list
class User(BaseModel):
    username: str
    password: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title="Movie Recommender API",
    description="API build up by Fernandez, Guillherme and Claudia powered by FastAPI.",
    version="1.0.1",
    openapi_tags=[
        {
            'name': 'home',
            'description': 'entry of the API'
        },
        {
            'name': 'movie_recommendation_via_user',
            'description': 'put the userId and get Top 5 recommended movies'
        },
        {
            'name': 'movie_recomendation_via_movie',
            'description': 'put the movieId and get Top 5 recommended movies'
        }
    ]
)

@app.get('/', tags=["home"])
def get_index():
    """Returns greetings
    """
    return {'greetings': 'welcome'}


@app.get("/movie_recommendation_via_user/{userId}", tags=["movie_recommendation_via_userId"])
def read_item(token: str = Depends(oauth2_scheme)):
    """
    In this endpoint the user will put the userId into the API and will return 5 movies
    which are most likely similiar rated by users therefore in the same cluster
    :param input_user:
    :return:
    """
    # generate recommendation using the model that we have trained
    prediction = generate_recommendation(svd, token, ratings_data, movies_data, 5)
    print(prediction)
    return [i[0] for i in prediction]

@app.get("/movie_recomendation_via_movie/{movieId}", tags=["movie_recommendation_via_movieID"])
def read_item(input_movie: int):
    """
    In this endpoint the user will put the movieId into the API and will return 5 movies
    which are similiar rated and therefore in the same cluster
    :param input_movie:
    :return:
    """
    input_movie = int(input_movie)
    #list of movies out of reco
    #list of recos -> ratings
    # return movie_reco_list
    pass

### user registration process  #####
def get_user(username: str):
    connection = sqlite3.connect("../data/movie.db")
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM users_db")
    rows = cursor.fetchall()
    users_list= [row for row in rows]
    if username in users_list:
        return username

def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(token)
    return user

def fake_hash_password(password: str):
    return password

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    connection = sqlite3.connect("../data/movie.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users_db")
    rows = cursor.fetchall()
    users_list= [row for row in rows]
    user_name = [x[0] for x in users_list if x[0] == form_data.username]
    print(user_name)
    if not user_name:
        raise HTTPException(status_code=400, detail="Incorrect username ")
    connection2 = sqlite3.connect("../data/movie.db")
    cursor2 = connection2.cursor()
    cursor2.execute(f"SELECT * FROM users_db")
    rows = cursor2.fetchall()
    passw_list= [row for row in rows]
    passw = [x[1] for x in passw_list if x[1] == form_data.password]
    if not passw[0] == form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {"access_token": user_name, "token_type": "bearer"}

@app.get("/users/", name='get all user')
def all_user(token: str = Depends(oauth2_scheme)):
    connection = sqlite3.connect("../data/movie.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users_db(username, password)")

    cursor.execute("SELECT username FROM users_db")
    rows = cursor.fetchall()
    users_list = [row for row in rows]
    return users_list

@app.put("/users/", name='register new user')
def set_new_user(user: User, token: str = Depends(oauth2_scheme)):
    print(token)
    if token=="admin":
        connection = sqlite3.connect("../data/movie.db")
        cursor = connection.cursor()
        print(user.username)
        query = f"INSERT INTO  users_db(username, password) VALUES (?, ?)"
        cursor.execute(query, (user.username, user.password))
        connection.commit()
    if token!= "admin":
            raise HTTPException(status_code=400, detail="not sufficient rights")

class Ratings(BaseModel):
    rating_1: int
    rating_2: int
    rating_3: int
    rating_4: int
    rating_5: int

@app.put("/ratings/", name='register new user ratings')
def set_ratings_to_recommended_movies(rating_1: Annotated[str, Form()],
                                      rating_2: Annotated[str, Form()],
                                      rating_3: Annotated[str, Form()],
                                      rating_4: Annotated[str, Form()],
                                      rating_5: Annotated[str, Form()],
                                      token: str = Depends(oauth2_scheme)):
    prediction = generate_recommendation(svd, token, ratings_data, movies_data, 5)
    prediction_movie_title = [i[0] for i in prediction]
    #sql append
    #[userid, movieid, rating]
    pred_ratings = [i[1] for i in prediction]
    user_ratings = [rating_1, rating_2, rating_3, rating_4, rating_5]
    movieid = [movies_data[movies_data["title"] == movie]["movieId"].item() for movie in prediction_movie_title]
    test = []
    rating_data_input= []
    for i in range(0,len(pred_ratings)):
        rating_list_for_db = [token[0], movieid[i], prediction_movie_title[i], pred_ratings[i], user_ratings[i]]
        test.append(rating_list_for_db)

    test_df = pd.DataFrame(test)
    print(test_df)
    test_df.to_sql('new_user_rating', con=engine, if_exists='append', index=False)

    for i in range(0,len(pred_ratings)):
        rating_list_for_db = [token[0], movieid[i], user_ratings[i], datetime.datetime.now()]
        rating_data_input.append(rating_list_for_db)
    rating_data_input_df = pd.DataFrame(rating_data_input)
    rating_data_input_df.to_sql('ratings', con=engine, if_exists='append', index=False)


    return {f"{prediction_movie_title[0]}": rating_1,
            f"{prediction_movie_title[1]}": rating_2,
            f"{prediction_movie_title[2]}": rating_3,
            f"{prediction_movie_title[3]}": rating_4,
            f"{prediction_movie_title[4]}": rating_5}


if __name__ == "__main__":
    # Run the FastAPI application on an Uvicorn server
    uvicorn.run(host="0.0.0.0")
