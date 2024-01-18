
import sys
import surprise
import pandas as pd

from recommenders.utils.timer import Timer
from recommenders.datasets.python_splitters import python_random_split
from recommenders.evaluation.python_evaluation import (
    rmse,
    mae,
    rsquared,
    exp_var,
    map_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    get_top_k_items,
)
from recommenders.models.surprise.surprise_utils import (
    predict,
    compute_ranking_predictions,
)
import importlib
import importlib_metadata as metadata
importlib.metadata = metadata


print(f"System version: {sys.version}")
print(f"Surprise version: {surprise.__version__}")

# Top k items to recommend
TOP_K = 10

# # Select MovieLens data size: 100k, 1m, 10m, or 20m
# MOVIELENS_DATA_SIZE = "100k"
#
# data = movielens.load_pandas_df(
#     size=MOVIELENS_DATA_SIZE, header=["userID", "itemID", "rating"]
# )
from sqlalchemy import create_engine
# Replace these with your actual database credentials
user = 'root'
password = 'password'
host = 'localhost'
database = 'movie'
# Create the MySQL engine
engine = create_engine(f'mysql://{user}:{password}@{host}/{database}')
#read data from DB
data = pd.read_sql_query("SELECT * FROM ratings ORDER BY timestamp", engine)
data = data[["user_id", "item_id", "rating"]]
data = data.rename(columns={"user_id":"userID", "item_id":"itemID"})
min_rating = data.rating.min()
max_rating = data.rating.max()
from surprise import Reader
reader = Reader(rating_scale=(min_rating, max_rating))

print(data.head())
train, test = python_random_split(data, 0.75)
print(train)
# 'reader' is being used to get rating scale (for MovieLens, the scale is [1, 5]).
# 'rating_scale' parameter can be used instead for the later version of surprise lib:
# https://github.com/NicolasHug/Surprise/blob/master/surprise/dataset.py
train_set = surprise.Dataset.load_from_df(
    train, reader=surprise.Reader("ml-100k")
).build_full_trainset()


svd = surprise.SVD(random_state=0, n_factors=200, n_epochs=30, verbose=True)

with Timer() as train_time:
    svd.fit(train_set)

print(f"Took {train_time.interval} seconds for training.")

predictions = predict(svd, test, usercol="userID", itemcol="itemID")

with Timer() as test_time:
    all_predictions = compute_ranking_predictions(
        svd, train, usercol="userID", itemcol="itemID", remove_seen=True
    )

print(f"Took {test_time.interval} seconds for prediction.")
print(all_predictions.head())



eval_rmse = rmse(test, predictions)
eval_mae = mae(test, predictions)
eval_rsquared = rsquared(test, predictions)
eval_exp_var = exp_var(test, predictions)

eval_map = map_at_k(test, all_predictions, col_prediction="prediction", k=TOP_K)
eval_ndcg = ndcg_at_k(test, all_predictions, col_prediction="prediction", k=TOP_K)
eval_precision = precision_at_k(
    test, all_predictions, col_prediction="prediction", k=TOP_K
)
eval_recall = recall_at_k(test, all_predictions, col_prediction="prediction", k=TOP_K)


print(
    "RMSE:\t\t%f" % eval_rmse,
    "MAE:\t\t%f" % eval_mae,
    "rsquared:\t%f" % eval_rsquared,
    "exp var:\t%f" % eval_exp_var,
    sep="\n",
)

print("----")

print(
    "MAP:\t\t%f" % eval_map,
    "NDCG:\t\t%f" % eval_ndcg,
    "Precision@K:\t%f" % eval_precision,
    "Recall@K:\t%f" % eval_recall,
    sep="\n",
)


from sqlalchemy import create_engine

# Replace these with your actual database credentials
user = 'root'
password = 'password'
host = 'localhost'
database = 'movie'

# Create the MySQL engine
engine = create_engine(f'mysql://{user}:{password}@{host}/{database}')
print("write to DB")
all_predictions = all_predictions.rename(columns={"userID": "userId","itemID": "movieId"})
all_predictions.to_sql('predictions', con=engine, if_exists='replace', index=False)