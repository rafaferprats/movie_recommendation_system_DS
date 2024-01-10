# Getting data

# The data used in this article is the open sourced dataset, which contains 100836 data points, by movielens.
# https://grouplens.org/datasets/movielens/

import pandas as pd
import numpy as np

from sqlalchemy import create_engine
engine = create_engine('sqlite:///../data/movie.db', echo=False)

#read data from DB

data = pd.read_sql_query("SELECT * FROM ratings", engine)

movies = pd.read_sql_query("SELECT * FROM movies", engine)

from surprise import SVD, Dataset, Reader
from surprise.accuracy import rmse
from collections import defaultdict

def get_top_n(predictions, n=10):
    """Return the top-N recommendation for each user from a set of predictions.
    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.
    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    """

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

# A reader is still needed but only the rating_scale param is requiered.
reader = Reader(rating_scale=(1, 5))

# The columns must correspond to user id, item id and ratings (in that order).
data = Dataset.load_from_df(data[['userId', 'movieId', 'rating']], reader)

# Load the movielens-100k dataset (download it if needed).
trainset = data.build_full_trainset()

# Use an example algorithm: SVD.
algo = SVD()
algo.fit(trainset)

# predict ratings for all pairs (u, i) that are in the training set.
testset = trainset.build_testset()
predictions = algo.test(testset)
rmse(predictions)

# we can now query for specific predicions
uid = str(196)  # raw user id (as in the ratings file). They are **strings**!
iid = str(302)  # raw item id (as in the ratings file). They are **strings**!

# get a prediction for specific users and items.
pred = algo.predict(uid, iid, r_ui=None, verbose=True)

#actual predictions as thse items have not been seen by the users. there is no ground truth.
# We predict ratings for all pairs (u, i) that are NOT in the training set.
testset = trainset.build_anti_testset()
predictions = algo.test(testset)
top_n = get_top_n(predictions, n=10)


from surprise import Dataset, KNNBasic

# Load the movielens-100k dataset
data = Dataset.load_builtin("ml-100k")

# Retrieve the trainset.
trainset = data.build_full_trainset()

# Build an algorithm, and train it.
algo = KNNBasic()
algo.fit(trainset)

uid = str(196)  # raw user id (as in the ratings file). They are **strings**!
iid = str(302)  # raw item id (as in the ratings file). They are **strings**!

# get a prediction for specific users and items.
pred = algo.predict(uid, iid, r_ui=4, verbose=True)

# Print the recommended items for each user
for uid, user_ratings in top_n.items():
    print(uid, [iid for (iid, _) in user_ratings])
    break