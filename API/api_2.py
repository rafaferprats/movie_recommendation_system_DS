import pandas as pd
import numpy as np
from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer,OAuth2PasswordRequestForm
import uvicorn
from pydantic import BaseModel
import sqlite3
from typing_extensions import Annotated
import datetime
import json


# load the data
from sqlalchemy import create_engine
user = 'root'
password = 'password'
host = 'localhost'
database = 'movie'
engine = create_engine(f'mysql://{user}:{password}@{host}/{database}')
import mysql.connector

connection = mysql.connector.connect(host='localhost',
                                     database='movie',
                                     user='root',
                                     password='password')


# read data from DB
ratings_data = pd.read_sql_query("SELECT * FROM ratings", engine)
movies_data = pd.read_sql_query("SELECT * FROM movies", engine)
predictions = pd.read_sql_query("SELECT * FROM predictions", engine)
new_ratings = pd.read_sql_query("SELECT * FROM new_user_rating", engine)
registered_user = pd.read_sql_query("SELECT * FROM users_db", engine)

class User(BaseModel):
    username: str
    password: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title="Movie Recommender API",
    description="API build up by Fernandez, Guillherme and Claudia powered by FastAPI.",
    version="1.0.1"
)

@app.get('/', tags=["home"])
def get_index():
    """Returns greetings
    """
    return {'greetings': 'welcome'}

@app.get("/movie_recommendation_via_user/{userId}", tags=["movie_recommendation_via_userId"])
def get_movie_reco(token: str = Depends(oauth2_scheme)):
    """
    In this endpoint the user will put the userId into the API and will return 5 movies
    which are most likely similiar rated by users therefore in the same cluster
    :param input_user:
    :return:
    """
    # generate recommendation using the model that we have trained
    user_prediction = predictions[predictions.userId == int(token[0])]
    user_prediction = user_prediction.sort_values(by="prediction",ascending=False)
    choice = user_prediction[:6]
    movies_data["movieId"] = movies_data["movieId"].astype(int)
    merged_choice = pd.merge(choice, movies_data, left_on='movieId', right_on='movieId', how='left')
    res = merged_choice[["movieId", "title"]].to_json(orient="records")
    parsed = json.loads(res)
    return parsed


### user registration process  #####
def get_user(username: str):
    connection = sqlite3.connect("../data/movie.db")
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM users_db")
    rows = cursor.fetchall()
    users_list= [row for row in rows]
    if username in users_list:
        return username


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = token[0]
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
        cursor = connection.cursor()
        if len(registered_user[registered_user["username"]==str(token[0])])==0:
            query = f"INSERT INTO  users_db(username, password) VALUES (%s, %s)"
            cursor.execute(query, (user.username, user.password))
            connection.commit()
        else:
            raise HTTPException(status_code=400, detail="user already exists")
    if token!= "admin":
            raise HTTPException(status_code=400, detail="not sufficient rights")

@app.put("/ratings/", name='register new user ratings')
def set_ratings_to_recommended_movies(rating_1: Annotated[str, Form()],
                                      rating_2: Annotated[str, Form()],
                                      rating_3: Annotated[str, Form()],
                                      rating_4: Annotated[str, Form()],
                                      rating_5: Annotated[str, Form()],
                                      token: str = Depends(oauth2_scheme)):

    user_prediction = predictions[predictions.userId == int(token[0])]
    user_prediction = user_prediction.sort_values(by="prediction", ascending=False)
    choice = user_prediction[:5]
    ratings_data.rename(columns={"user_id": "userId", "item_id": "movieId"}, inplace=True)
    new_ratings["movieId"] = new_ratings["movieId"].astype(int)
    print("new_ratings", new_ratings)
    df = pd.merge(choice[["userId", "movieId"]], new_ratings[["userId", "movieId", "title"]], on=["userId", "movieId"],
                  how='left', indicator='Exist')
    df['Exist'] = np.where(df.Exist == 'both', True, False)
    for i in range(0, len(df)):
        if df.iloc[i]["Exist"] == True:
            raise HTTPException(status_code=400, detail=f"you've rated already your recommendation")
        else:
            merged_choice = pd.merge(choice, movies_data, left_on='movieId', right_on='movieId', how='left')
            print(merged_choice)
            prediction_movie_title = [merged_choice.iloc[i]["title"] for i in range(0,len(merged_choice))]
            print(prediction_movie_title)
            #sql append
            #[userid, movieid, rating]
            pred_ratings = [choice.iloc[i].prediction for i in range(0,len(choice))]
            user_ratings = [rating_1, rating_2, rating_3, rating_4, rating_5]
            movieid = [choice.iloc[i].movieId for i in range(0,len(choice))]
            test = []
            rating_data_input= []
            for i in range(0,len(pred_ratings)):
                rating_list_for_db = [token[0], movieid[i], prediction_movie_title[i], pred_ratings[i], user_ratings[i]]
                test.append(rating_list_for_db)

            test_df = pd.DataFrame(test, columns=["userId", "movieId", "title", "preds_rating", "rating"])
            print(test_df)
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS new_user_rating(userId INT, movieId INT, title VARCHAR(120), preds_rating FLOAT, rating FLOAT)")
            test_df.to_sql('new_user_rating', con=engine, if_exists='append', index=False)

            for i in range(0,len(pred_ratings)):
                rating_list_for_db = [token[0], movieid[i], user_ratings[i], datetime.datetime.now()]
                rating_data_input.append(rating_list_for_db)
            rating_data_input_df = pd.DataFrame(rating_data_input, columns=["user_id", "item_id", "rating", "timestamp"])
            rating_data_input_df.to_sql('ratings', con=engine, if_exists='append', index=False)

        return {f"{prediction_movie_title[0]}": rating_1,
                f"{prediction_movie_title[1]}": rating_2,
                f"{prediction_movie_title[2]}": rating_3,
                f"{prediction_movie_title[3]}": rating_4,
                f"{prediction_movie_title[4]}": rating_5}


if __name__ == "__main__":
    # Run the FastAPI application on an Uvicorn server
    uvicorn.run(app,host="0.0.0.0")
