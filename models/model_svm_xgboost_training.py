# Getting data

# The data used in this article is the open sourced dataset, which contains 100836 data points, by movielens.
# https://grouplens.org/datasets/movielens/


import pandas as pd
data = pd.read_csv("../data/ml-latest-small/ratings.csv")

movies = pd.read_csv("../data/ml-latest-small/movies.csv")

data = data.drop('timestamp',axis=1)
print(data.shape)


#splitting the data
train_data=data.iloc[:int(data.shape[0]*0.80)]
test_data=data.iloc[int(data.shape[0]*0.80):]


# SVD MF
#
# http://surprise.readthedocs.io/en/stable/matrix_factorization.html#surprise.prediction_algorithms.matrix_factorization.SVD
#
# __ Predicted Rating : __
#
# 𝑟̂ 𝑢𝑖=𝜇+𝑏𝑢+𝑏𝑖+𝑞𝑇𝑖𝑝𝑢
# 𝑞𝑞𝑖 - Representation of item(movie) in latent factor space
#
# 𝑝𝑝𝑢 - Representation of user in new latent factor space
#
# A BASIC MATRIX FACTORIZATION MODEL in https://datajobs.com/data-science-repo/Recommender-Systems-[Netflix].pdf
# Optimization problem with user item interactions and regularization (to avoid overfitting)
# ∑𝑟𝑢𝑖∈𝑅𝑡𝑟𝑎𝑖𝑛(𝑟𝑢𝑖−𝑟̂ 𝑢𝑖)2+𝜆(𝑏2𝑖+𝑏2𝑢+||𝑞𝑖||2+||𝑝𝑢||2)

from surprise import SVD
import numpy as np
from surprise import Reader, Dataset

# train set from train data

# It is to specify how to read the dataframe.
# for our dataframe, we don't have to specify anything extra..
reader = Reader(rating_scale=(1,5))

# create the traindata from the dataframe...
train_data_mf = Dataset.load_from_df(train_data[['userId', 'movieId', 'rating']], reader)

# build the trainset from traindata.., It is of dataset format from surprise library..
trainset = train_data_mf.build_full_trainset()

#test set from test data

# It is to specify how to read the dataframe.
# for our dataframe, we don't have to specify anything extra..
reader = Reader(rating_scale=(1,5))

# create the traindata from the dataframe...
test_data_mf = Dataset.load_from_df(test_data[['userId', 'movieId', 'rating']], reader)

# build the trainset from traindata.., It is of dataset format from surprise library..
testset = test_data_mf.build_full_trainset()

svd = SVD(n_factors=100, biased=True, random_state=15, verbose=True)
svd.fit(trainset)

# storing train predictions

#getting predictions of trainset
train_preds = svd.test(trainset.build_testset())

train_pred_mf = np.array([pred.est for pred in train_preds])


# storing test predictions

#getting predictions of trainset
test_preds = svd.test(testset.build_testset())

test_pred_mf = np.array([pred.est for pred in test_preds])


# XGBoost

# Preparing train data frame

from scipy import sparse
# Creating a sparse matrix
train_sparse_matrix = sparse.csr_matrix((train_data.rating.values, (train_data.userId.values,
                                               train_data.movieId.values)))

# Global avg of all movies by all users

train_averages = dict()
# get the global average of ratings in our train set.
train_global_average = train_sparse_matrix.sum()/train_sparse_matrix.count_nonzero()
train_averages['global'] = train_global_average


# get the user averages in dictionary (key: user_id/movie_id, value: avg rating)

def get_average_ratings(sparse_matrix, of_users):

    # average ratings of user/axes
    ax = 1 if of_users else 0 # 1 - User axes,0 - Movie axes

    # ".A1" is for converting Column_Matrix to 1-D numpy array
    sum_of_ratings = sparse_matrix.sum(axis=ax).A1
    # Boolean matrix of ratings ( whether a user rated that movie or not)
    is_rated = sparse_matrix!=0
    # no of ratings that each user OR movie..
    no_of_ratings = is_rated.sum(axis=ax).A1

    # max_user  and max_movie ids in sparse matrix
    u,m = sparse_matrix.shape
    # creae a dictonary of users and their average ratings..
    average_ratings = { i : sum_of_ratings[i]/no_of_ratings[i]
                                 for i in range(u if of_users else m)
                                    if no_of_ratings[i] !=0}

    # return that dictionary of average ratings
    return average_ratings

# Average ratings given by a user

train_averages['user'] = get_average_ratings(train_sparse_matrix, of_users=True)
print('\nAverage rating of user 10 :',train_averages['user'][10])
print('\nAverage rating of user 1 :',train_averages['user'][1])


# Average ratings given for a movie

train_averages['movie'] =  get_average_ratings(train_sparse_matrix, of_users=False)
print('\n AVerage rating of movie 15 :',train_averages['movie'][15])

# get users, movies and ratings from our samples train sparse matrix
train_users, train_movies, train_ratings = sparse.find(train_sparse_matrix)

from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
final_data = pd.DataFrame()
count = 0
for (user, movie, rating)  in zip(train_users, train_movies, train_ratings):
            start = datetime.now()
        #     print(user, movie)
            #--------------------- Ratings of "movie" by similar users of "user" ---------------------
            # compute the similar Users of the "user"
            user_sim = cosine_similarity(train_sparse_matrix[user], train_sparse_matrix).ravel()
            top_sim_users = user_sim.argsort()[::-1][1:] # we are ignoring 'The User' from its similar users.
            # get the ratings of most similar users for this movie
            top_ratings = train_sparse_matrix[top_sim_users, movie].toarray().ravel()
            # we will make it's length "5" by adding movie averages to .
            top_sim_users_ratings = list(top_ratings[top_ratings != 0][:5])
            top_sim_users_ratings.extend([train_averages['movie'][movie]]*(5 - len(top_sim_users_ratings)))
        #     print(top_sim_users_ratings, end=" ")


            #--------------------- Ratings by "user"  to similar movies of "movie" ---------------------
            # compute the similar movies of the "movie"
            movie_sim = cosine_similarity(train_sparse_matrix[:,movie].T, train_sparse_matrix.T).ravel()
            top_sim_movies = movie_sim.argsort()[::-1][1:] # we are ignoring 'The User' from its similar users.
            # get the ratings of most similar movie rated by this user..
            top_ratings = train_sparse_matrix[user, top_sim_movies].toarray().ravel()
            # we will make it's length "5" by adding user averages to.
            top_sim_movies_ratings = list(top_ratings[top_ratings != 0][:5])
            top_sim_movies_ratings.extend([train_averages['user'][user]]*(5-len(top_sim_movies_ratings)))
        #     print(top_sim_movies_ratings, end=" : -- ")

            #-----------------prepare the row to be stores in a file-----------------#
            row = list()
            row.append(user)
            row.append(movie)
            # Now add the other features to this data...
            row.append(train_averages['global']) # first feature
            # next 5 features are similar_users "movie" ratings
            row.extend(top_sim_users_ratings)
            # next 5 features are "user" ratings for similar_movies
            row.extend(top_sim_movies_ratings)
            # Avg_user rating
            row.append(train_averages['user'][user])
            # Avg_movie rating
            row.append(train_averages['movie'][movie])

            # finalley, The actual Rating of this user-movie pair...
            row.append(rating)
            count = count + 1
            final_data = final_data.append([row])
            #print(count)



            if (count)%10000 == 0:
                # print(','.join(map(str, row)))
                print("Done for {} rows----- {}".format(count, datetime.now() - start))


final_data.columns=['user', 'movie', 'GAvg', 'sur1', 'sur2', 'sur3', 'sur4', 'sur5',
            'smr1', 'smr2', 'smr3', 'smr4', 'smr5', 'UAvg', 'MAvg', 'rating']

final_data['mf_svd']=train_pred_mf

print("final_data", final_data.head())

# Preparing test data

(test_data.rating.values, (test_data.userId.values,
                                               test_data.movieId.values))

# Creating a sparse matrix
test_sparse_matrix = sparse.csr_matrix((test_data.rating.values, (test_data.userId.values,
                                               test_data.movieId.values)))

# Global avg of all movies by all users

test_averages = dict()
# get the global average of ratings in our train set.
test_global_average = test_sparse_matrix.sum()/test_sparse_matrix.count_nonzero()
test_averages['global'] = test_global_average


# get the user averages in dictionary (key: user_id/movie_id, value: avg rating)

def get_average_ratings(sparse_matrix, of_users):

    # average ratings of user/axes
    ax = 1 if of_users else 0 # 1 - User axes,0 - Movie axes

    # ".A1" is for converting Column_Matrix to 1-D numpy array
    sum_of_ratings = sparse_matrix.sum(axis=ax).A1
    # Boolean matrix of ratings ( whether a user rated that movie or not)
    is_rated = sparse_matrix!=0
    # no of ratings that each user OR movie..
    no_of_ratings = is_rated.sum(axis=ax).A1

    # max_user  and max_movie ids in sparse matrix
    u,m = sparse_matrix.shape
    # creae a dictonary of users and their average ratigns..
    average_ratings = { i : sum_of_ratings[i]/no_of_ratings[i]
                                 for i in range(u if of_users else m)
                                    if no_of_ratings[i] !=0}

    # return that dictionary of average ratings
    return average_ratings




# Average ratings given by a user

test_averages['user'] = get_average_ratings(test_sparse_matrix, of_users=True)
#print('\nAverage rating of user 10 :',test_averages['user'][10])

# Average ratings given for a movie

test_averages['movie'] =  get_average_ratings(test_sparse_matrix, of_users=False)
print('\n AVerage rating of movie 15 :',test_averages['movie'][15])

# get users, movies and ratings from our samples train sparse matrix
test_users, test_movies, test_ratings = sparse.find(test_sparse_matrix)

final_test_data = pd.DataFrame()
count = 0
for (user, movie, rating)  in zip(test_users, test_movies, test_ratings):
            st = datetime.now()
        #     print(user, movie)
            #--------------------- Ratings of "movie" by similar users of "user" ---------------------
            # compute the similar Users of the "user"
            user_sim = cosine_similarity(test_sparse_matrix[user], test_sparse_matrix).ravel()
            top_sim_users = user_sim.argsort()[::-1][1:] # we are ignoring 'The User' from its similar users.
            # get the ratings of most similar users for this movie
            top_ratings = test_sparse_matrix[top_sim_users, movie].toarray().ravel()
            # we will make it's length "5" by adding movie averages to .
            top_sim_users_ratings = list(top_ratings[top_ratings != 0][:5])
            top_sim_users_ratings.extend([test_averages['movie'][movie]]*(5 - len(top_sim_users_ratings)))
        #     print(top_sim_users_ratings, end=" ")


            #--------------------- Ratings by "user"  to similar movies of "movie" ---------------------
            # compute the similar movies of the "movie"
            movie_sim = cosine_similarity(test_sparse_matrix[:,movie].T, test_sparse_matrix.T).ravel()
            top_sim_movies = movie_sim.argsort()[::-1][1:] # we are ignoring 'The User' from its similar users.
            # get the ratings of most similar movie rated by this user..
            top_ratings = test_sparse_matrix[user, top_sim_movies].toarray().ravel()
            # we will make it's length "5" by adding user averages to.
            top_sim_movies_ratings = list(top_ratings[top_ratings != 0][:5])
            top_sim_movies_ratings.extend([test_averages['user'][user]]*(5-len(top_sim_movies_ratings)))
        #     print(top_sim_movies_ratings, end=" : -- ")

            #-----------------prepare the row to be stores in a file-----------------#
            row = list()
            row.append(user)
            row.append(movie)
            # Now add the other features to this data...
            row.append(test_averages['global']) # first feature
            # next 5 features are similar_users "movie" ratings
            row.extend(top_sim_users_ratings)
            # next 5 features are "user" ratings for similar_movies
            row.extend(top_sim_movies_ratings)
            # Avg_user rating
            row.append(test_averages['user'][user])
            # Avg_movie rating
            row.append(test_averages['movie'][movie])

            # finalley, The actual Rating of this user-movie pair...
            row.append(rating)
            count = count + 1
            final_test_data = final_test_data.append([row])
            print(count)



            if (count)%10000 == 0:
                # print(','.join(map(str, row)))
                print("Done for {} rows----- {}".format(count, datetime.now() - start))


final_test_data.columns=['user', 'movie', 'GAvg', 'sur1', 'sur2', 'sur3', 'sur4', 'sur5',
            'smr1', 'smr2', 'smr3', 'smr4', 'smr5', 'UAvg', 'MAvg', 'rating']


final_test_data['mf_svd']=test_pred_mf


# creating XGBoost

def get_error_metrics(y_true, y_pred):
    rmse = np.sqrt(np.mean([ (y_true[i] - y_pred[i])**2 for i in range(len(y_pred)) ]))
    mape = np.mean(np.abs( (y_true - y_pred)/y_true )) * 100
    return rmse, mape

# prepare train data
x_train = final_data.drop(['user', 'movie','rating'], axis=1)
y_train = final_data['rating']

# Prepare Test data
x_test = final_test_data.drop(['user','movie','rating'], axis=1)
y_test = final_test_data['rating']

import xgboost as xgb


# initialize XGBoost model...
xgb_model = xgb.XGBRegressor(silent=False, n_jobs=13, random_state=15, n_estimators=100)
# dictionaries for storing train and test results
train_results = dict()
test_results = dict()


# fit the model
print('Training the model..')
start =datetime.now()
xgb_model.fit(x_train, y_train, eval_metric = 'rmse')
print('Done. Time taken : {}\n'.format(datetime.now()-start))
print('Done \n')



# from the trained model, get the predictions....
print('Evaluating the model with TRAIN data...')
start =datetime.now()
y_train_pred = xgb_model.predict(x_train)
# get the rmse and mape of train data...
rmse_train, mape_train = get_error_metrics(y_train.values, y_train_pred)

# store the results in train_results dictionary..
train_results = {'rmse': rmse_train,
                    'mape' : mape_train,
                    'predictions' : y_train_pred}

print("train_results", train_results)


#######################################
# get the test data predictions and compute rmse and mape
print('Evaluating Test data')
y_test_pred = xgb_model.predict(x_test)
rmse_test, mape_test = get_error_metrics(y_true=y_test.values, y_pred=y_test_pred)
# store them in our test results dictionary.
test_results = {'rmse': rmse_test,
                    'mape' : mape_test,
                    'predictions':y_test_pred}

print("test_results", test_results)

