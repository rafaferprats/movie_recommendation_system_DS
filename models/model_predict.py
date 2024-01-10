import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
engine = create_engine('sqlite:///../data/movie.db', echo=False)

#read data from DB

ratings_data = pd.read_sql_query("SELECT * FROM ratings", engine)
movies_data = pd.read_sql_query("SELECT * FROM movies", engine)

##### Prepare Dataset ######
from surprise import Dataset
from surprise import Reader

# Get minimum and maximum rating from the dataset
min_rating = ratings_data.rating.min()
max_rating = ratings_data.rating.max()

reader = Reader(rating_scale=(min_rating, max_rating))
data = Dataset.load_from_df(ratings_data[['userId', 'movieId', 'rating']], reader)


####modeling####
from surprise import SVD
from surprise.model_selection import cross_validate

svd = SVD(n_epochs=10)
results = cross_validate(svd, data, measures=['RMSE', 'MAE'], cv=10, verbose=True)


##### Hyperparameter Tuning #####
from surprise import SVD
from surprise.model_selection import GridSearchCV

param_grid = {
    'n_factors': [20, 50, 100],
    'n_epochs': [5, 10, 20]
}

gs = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=10)
gs.fit(data)

print(gs.best_score['rmse'])
print(gs.best_params['rmse'])

from surprise.model_selection import train_test_split

# best hyperparameters
best_factor = gs.best_params['rmse']['n_factors']
best_epoch = gs.best_params['rmse']['n_epochs']

# sample random trainset and testset
# test set is made of 20% of the ratings.
trainset, testset = train_test_split(data, test_size=.20)

# We'll use the famous SVD algorithm.
svd = SVD(n_factors=best_factor, n_epochs=best_epoch)

# Train the algorithm on the trainset
svd.fit(trainset)


#####prediction#####
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


# define which user ID that we want to give recommendation
userID = 1
# define how many top-n movies that we want to recommend
n_items = 5
# generate recommendation using the model that we have trained
print(generate_recommendation(svd, userID, ratings_data, movies_data, n_items))


#### dump model ####
import pickle
# To save
pkl_filename = "svd_model.pkl"
with open(pkl_filename, 'wb') as file:
    pickle.dump(svd, file)