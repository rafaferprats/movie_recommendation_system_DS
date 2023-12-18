import pandas as pd
import pickle
from fastapi import FastAPI
from collections import Counter
import uvicorn

app = FastAPI(
    title="Movie Recommender API",
    description="API build up by Fernandez, Guillherme and Claudia powered by FastAPI.",
    version="1.0.1",
    openapi_tags = [
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

refined_dataset = pd.read_csv("../data/final_db.csv")
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
    
@app.get("/movie_recommendation_via_user/{userId}", tags=["movie_recommendation_via_userId"])
def read_item(input_user: int):
    """
    In this endpoint the user will put the userId into the API and will return 5 movies
    which are most likely similiar rated by users therefore in the same cluster
    :param input_user:
    :return:
    """
    input_user = int(input_user)
    cluster_users = refined_dataset.loc[refined_dataset['userId'] == input_user, 'loc_clusters_users']
    cluster_users = Counter(cluster_users).most_common(1)[0] # 4, 6 times
    
    users = refined_dataset.loc[refined_dataset['loc_clusters_users'] == cluster_users[0], 'userId']
    users_list = users.tolist()
    list_movie_id = []
    list_movies_title = []

    for c in users_list:
            movie = refined_dataset.loc[refined_dataset['movieId'] == users.iloc[c]]
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
    
    
@app.get("/movie_recomendation_via_movie/{movieId}", tags=["movie_recommendation_via_movieID"])
def read_item(input_movie: int):
    """
    In this endpoint the user will put the movieId into the API and will return 5 movies
    which are similiar rated and therefore in the same cluster
    :param input_movie:
    :return:
    """
    input_movie = int(input_movie)
    cluster_movies = refined_dataset.loc[refined_dataset['movieId'] == input_movie, 'loc_clusters_movies']
    cluster_movies = Counter(cluster_movies).most_common(1)[0] # 4, 6 times


    movie_reco_df = []
    movies = refined_dataset.loc[refined_dataset['loc_clusters_movies'] == cluster_movies[0], 'movieId']
    list_movies_title = []
    list_movie_id = []
    for c in range(len(movies)):
        if movies.iloc[c] == int(input_movie):
            continue
        else:
            movie = refined_dataset.loc[refined_dataset['movieId'] == movies.iloc[c]]
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
    
   
    
if __name__ == "__main__":
    # Run the FastAPI application on an Uvicorn server
    uvicorn.run("main:app", port=5500, reload=False)  # nosec