import pandas as pd
from collections import Counter
import os
import uvicorn

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title="Movie Recommender API",
    description="API build up by Fernandez, Guillherme and Claudia powered by FastAPI.",
    version="1.0.1",
    openapi_tags = [
        {
            'name': 'home',
            'description': 'entry of the API'
        }
    ]
    )
    
    
#if you want to run the app with docker use this line
#final_db = pd.read_csv("final_db.csv")

#if you want to run the app to test the api use this line
n_retrain = 0
final_db = pd.read_csv("data/final_db.csv")
retrain_path = 'addon/retrain_models.py'
evaluation_dash_path = 'addon/evaluation_dash.py'
user_data = pd.read_csv("data/user_db.csv")
# user input via API
# df = pd.DataFrame(np.array([[userId, rating]]),
#                   columns=['userId', 'rating'])
# predict
#load model
# kmeans_movie = pickle.load(open('../models/kmeans_movie.pkl', 'rb'))
# cluster_movies = kmeans_movie.predict(df)

# API Root
@app.get('/', tags= ["home"])
def get_index():
    """Returns greetings
    """
    return {'greetings': 'welcome'}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_name = int(user_data[user_data["userId"] == int(form_data.username)]["userId"].values)
    print(user_name)
    if not user_name == int(form_data.username):
        raise HTTPException(status_code=400, detail="Incorrect username ")
    passw = user_data[user_data["userId"] == int(form_data.username)]["password"].values[0]
    if not passw == form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {"access_token": user_name, "token_type": "bearer"}

    
@app.get("/movie_recommendation_via_user", tags=["movie_recommendation_via_userId"]) #/{input_user}
def get_movie_from_user(token: str = Depends(oauth2_scheme)): #input_user: int,
    """
    In this endpoint the user will put the userId into the API and will return 5 movies
    which are most likely similiar rated by users therefore in the same cluster
    :param input_user:
    :return:
    """
    # input_user = int(input_user)
    cluster_users = final_db.loc[final_db['userId'] == int(token[0]), 'loc_clusters_users']
    cluster_users = Counter(cluster_users).most_common(1)[0] # 4, 6 times
    
    users = final_db.loc[final_db['loc_clusters_users'] == cluster_users[0], 'userId']
    users_list = users.tolist()
    list_movie_id = []
    list_movies_title = []

    for c in users_list:
            movie = final_db.loc[final_db['movieId'] == users.iloc[c]]
            if len(movie) != 0:
                movie_data = movie.iloc[0]
                movie_title = movie_data.title
                movie_id = movie_data.movieId
                list_movie_id.append(movie_id)
                list_movies_title.append(movie_title)
            #print('Recommended movie title:', movie_reco.iloc[0])
            #print('Recommended movie id:', movie_id.iloc[0])


    movie_reco_df = pd.DataFrame(list(zip(list_movies_title, list_movie_id)), columns=['list_movies_title', 'list_movie_id'])
    movie_reco_df = movie_reco_df.drop_duplicates()
    movie_reco_list = movie_reco_df.sample(n=5) 
    return movie_reco_list['list_movies_title']
    
    
@app.get("/movie_recomendation_via_movie/{input_movie}")
def get_movie_from_movie(input_movie: int, token: str = Depends(oauth2_scheme)):
    """
    In this endpoint the user will put the movieId into the API and will return 5 movies
    which are similiar rated and therefore in the same cluster
    :param input_movie:
    :return:
    """
    input_movie = int(input_movie)
    cluster_movies = final_db.loc[final_db['movieId'] == input_movie, 'loc_clusters_movies']
    cluster_movies = Counter(cluster_movies).most_common(1)[0] # 4, 6 times


    movie_reco_df = []
    movies = final_db.loc[final_db['loc_clusters_movies'] == cluster_movies[0], 'movieId']
    list_movies_title = []
    list_movie_id = []
    for c in range(len(movies)):
        if movies.iloc[c] == int(input_movie):
            continue
        else:
            movie = final_db.loc[final_db['movieId'] == movies.iloc[c]]
            movie_data = movie.iloc[0]
            movie_title = movie_data.title
            movie_id = movie_data.movieId
            list_movie_id.append(movie_id)
            list_movies_title.append(movie_title)
            #print('Recommended movie title:', movie_reco.iloc[0])
            #print('Recommended movie id:', movie_id.iloc[0])


    movie_reco_df = pd.DataFrame(list(zip(list_movies_title, list_movie_id)), columns=['list_movies_title', 'list_movie_id']) 
    movie_reco_list = movie_reco_df.sample(n=5) 
    return movie_reco_list['list_movies_title']

@app.put("/users/", name='register new user')
def set_new_user(user: User, token: str = Depends(oauth2_scheme)):
    user_data = pd.read_csv("data/user_db.csv")
    if (len(user_data[user_data["userId"]==user.username])) ==0:
        new_row = pd.DataFrame({'userId': user.username, 'password': user.password}, index=[0])
        user_data = pd.concat([new_row,user_data.loc[:]])
        user_data.to_csv('data/user_db.csv', sep=',', encoding='utf-8', index=False)
    else:
        raise HTTPException(status_code=400, detail="user already exists")

@app.get("/check_user_exist/{userId_check}")
def check_user_exist(token: str = Depends(oauth2_scheme)): #userId_check: int,
    """
    In this endpoint we can check if a userId exists in the DB
    :param userId_check:
    :return:
    """
    global final_db
    try:
        check_user = final_db.loc[final_db['userId'] == int(token[0]), 'userId'].iloc[0]
        return {'userId as': int(check_user),
                'We have that user in our DB':'',}
    except:
        return {'We dont have that user in our DB'}
        
@app.get("/check_movie_exist/{movieId_check}")
def check_movie_exist(movieId_check: int, token: str = Depends(oauth2_scheme)):
    """
    In this endpoint we can check if a movieId exists in the DB
    :param movieId_check:
    :return:
    """
    global final_db
    try:
        check_movie = final_db.loc[final_db['movieId'] == movieId_check, 'movieId'].iloc[0]
        title_check = final_db.loc[final_db['movieId'] == movieId_check, 'title'].iloc[0]
        return {'movieId as': int(check_movie),
                'We have that movie in our DB as':title_check,}
    except:
        return {'We dont have that movie in our DB'}
    
@app.get("/add_user/movieid/{movieId_new_row}/rating/{rating_score_new_row}")
def add_user(movieId_new_row: int, rating_score_new_row: float, token: str = Depends(oauth2_scheme)):
    """
    In this endpoint we can add a new user, moviedId, and a rate of the movie in the DB
    :param movieId_new_row, rating_score_new_row:
    :return:
    """
    global final_db, n_retrain
    new_user_id =  int(final_db['userId'].max() + 1)

    try:
        title_new_rating = final_db.loc[final_db['movieId'] == movieId_new_row, 'title']
        #print(title_new_rating.iloc[0])
        #print(new_user_id)
        #print(movieId_new_row)
        #print(final_db.info())
        title_str = title_new_rating.iloc[0]

        new_row = {'userId': new_user_id, 'title': title_str, 'movieId': movieId_new_row, 'rating': rating_score_new_row, 'loc_clusters_users': movieId_new_row, 'loc_clusters_movies': movieId_new_row}
        #print(new_row)
        #final_db = final_db.append(new_row, ignore_index=True)

        new_row = pd.DataFrame({'userId': new_user_id, 'title': title_str, 'movieId': movieId_new_row, 'rating': rating_score_new_row, 'loc_clusters_users': movieId_new_row, 'loc_clusters_movies': movieId_new_row}, index=[0])
        final_db = pd.concat([new_row,final_db.loc[:]])
        if n_retrain == 5:
            n_retrain = 0
            final_df = final_db[['userId', 'title', 'movieId', 'rating']].copy()
            print('Retraining the model with the new user . ')
            print('Retraining the model with the new user ..')
            print('Retraining the model with the new user ... waiting retrain time')
            final_df.to_csv('data/refined_dataset.csv', sep=',', encoding='utf-8')
            os.system(f'python {retrain_path}')
            print('Creating Evaluation dashboard with the new data ... ')
            os.system(f'python {evaluation_dash_path}')
        else:
            print('next retrain when you add ', 5- n_retrain, ' rating more')
            n_retrain = n_retrain + 1


        return {'new userId as': int(new_user_id),
                'movieId': int(movieId_new_row),
                'movie title': str(title_str),
                'rating score': float(rating_score_new_row),
                'the user has been': 'added to our DB',}
    except:
        return {'We dont have that movie in our DB'}
    
@app.get("/userid/{userId_new_row}/movieid/{movieId_new_row}/rating/{rating_score_new_row}")
def user_add_rating( movieId_new_row: int, rating_score_new_row: float, token: str = Depends(oauth2_scheme)): #userId_new_row:int,
    """
    In this endpoint a specific user can add a moviedId and a rate of the movie in the DB
    :param userId_new_row, movieId_new_row, rating_score_new_row:
    :return:
    """
    global final_db, n_retrain
    try:
        # user_new_rating = final_db.loc[final_db['userId'] == userId_new_row, 'userId'].iloc[0]
        user_new_rating = final_db.loc[final_db['userId'] == int(token[0]), 'userId'].iloc[0]
        title_new_rating = final_db.loc[final_db['movieId'] == movieId_new_row, 'title']
        title_str = title_new_rating.iloc[0]
        new_row = pd.DataFrame({'userId': user_new_rating, 'title': title_str, 'movieId': movieId_new_row, 'rating': rating_score_new_row, 'loc_clusters_users': user_new_rating, 'loc_clusters_movies': user_new_rating}, index=[0])
        final_db = pd.concat([new_row,final_db.loc[:]])
        if n_retrain == 5:
            n_retrain = 0
            final_df = final_db[['userId', 'title', 'movieId', 'rating']].copy()
            print('Retraining the model with the new data . ')
            print('Retraining the model with the new data ..')
            print('Retraining the model with the new data ... waiting retrain time')
            final_df.to_csv('data/refined_dataset.csv', sep=',', encoding='utf-8')
            os.system(f'python {retrain_path}')
            print('Creating Evaluation dashboard with the new data ... ')
            os.system(f'python {evaluation_dash_path}')
        else:
            print('next retrain when you add ', 5- n_retrain, ' rating more')
            n_retrain = n_retrain + 1
        return {'userId as': int(user_new_rating),
                'movieId': int(movieId_new_row),
                'movie title': str(title_str),
                'rating score': float(rating_score_new_row),
                'the movie has been rated': 'and added to our DB',}
            
    except:
        return {'We dont have that movie added or that user, please check other endpoint to check the userid or movieid'}

@app.get("/show_db_data/")
def show_db_data(token: str = Depends(oauth2_scheme)):
    """
    In this endpoint a we can check the numbers of users, movies and ratings
    :param:
    :return:
    """
    global final_db
    rating_count_df = pd.DataFrame(final_db.groupby(['rating']).size(), columns=['count'])
    num_users = final_db['userId'].nunique()
    num_items = final_db['title'].nunique()

    return {'The numbers of users in db are: ': int(num_users),
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
            'rating of the movies with 5': int(rating_count_df['count'].iloc[9]),}
    
@app.get("/show_scores/")
def show_scores_data(token: str = Depends(oauth2_scheme)):
    """
    In this endpoint a we can check the numbers of users, movies and ratings
    :param:
    :return:
    """
    
    scores_data = pd.read_csv("data/movie_reco_scores.csv")    
    sco_label = scores_data.columns.tolist()
    sco_retrain = scores_data.iloc[0].tolist()
    
    
    return {'Labels: ': sco_label,
            'Values: ': sco_retrain,}
            
          

@app.get("/delete_user/{userId_removed}")
async def delete_user(userId_removed:int, token: str = Depends(oauth2_scheme)):
    """
    In this endpoint we can check if a userId exists in the DB to remove it
    :param userId_check:
    :return:
    """
    global final_db
    if token == "999999":
        try:
            db_len = len(final_db)
            final_db.drop(final_db.index[final_db['userId'] == userId_removed], inplace=True)

            if len(final_db) == db_len:
                return {'We dont have that user in our DB, try another one'}
            else:
                return {'userId as': int(userId_removed),
                    'The user has been removed from our DB ':' ',}
        except:
            return {'We dont have that user in our DB'}
    if token != "999999":
            raise HTTPException(status_code=400, detail="not sufficient rights")
        
@app.get("/delete_movie/{movieId_removed}")
async def delete_movie(movieId_removed:int, token: str = Depends(oauth2_scheme)):
    """
    In this endpoint we can check if a userId exists in the DB to remove it
    :param userId_check:
    :return:
    """
    global final_db
    if token == "999999":
        try:
            db_len = len(final_db)
            title_check = final_db.loc[final_db['movieId'] == movieId_removed, 'title'].iloc[0]
            final_db.drop(final_db.index[final_db['movieId'] == movieId_removed], inplace=True)
            if len(final_db) == db_len:
                return {'We dont have that movie in our DB, try another one'}
            else:
                return {'movieId as': int(movieId_removed),
                    'The movie with the following title has been removed from our DB -> ':title_check,}
        except:
            return {'We dont have that movie in our DB'}
    if token != "999999":
            raise HTTPException(status_code=400, detail="not sufficient rights")
   

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port="$PORT")
    