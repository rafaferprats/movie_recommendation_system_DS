import pandas as pd
import pickle
from fastapi import FastAPI
from collections import Counter

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

refined_dataset = pd.read_csv("../data/refined_dataset.csv")
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
    cluster_users = Counter(cluster_users).most_common(1)[0]  # 4, 6 times
    cluster_users[0]

    users = refined_dataset.loc[refined_dataset['loc_clusters_users'] == cluster_users[0], 'userId']
    list_movies = []
    for c in range(1000):
        if users.iloc[c] == input_user:
            continue
        else:
            movie1 = refined_dataset.loc[refined_dataset['movieId'] == users.iloc[c]]
            movie1 = movie1['title']
            movie1 = movie1.iloc[1]
            list_movies.append(movie1)
    uniqueElements = list(set(list_movies))
    return uniqueElements[0:5]


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
    cluster_movies = Counter(cluster_movies).most_common(1)[0]  # 4, 6 times
    cluster_movies[0]
    movies = refined_dataset.loc[refined_dataset['loc_clusters_movies'] == cluster_movies[0], 'movieId']
    movie_selection= list()
    for c in range(5):
        if movies.iloc[c] == input_movie:
            continue
        else:
            movie1 = refined_dataset.loc[refined_dataset['movieId'] == movies.iloc[c]]
            movie1 = movie1['title']
            movie_selection.append(movie1.iloc[1])
    return movie_selection

