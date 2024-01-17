import os
import numpy as np
import pandas as pd
import pickle
from sklearn.cluster import KMeans
from collections import Counter
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import calinski_harabasz_score
import time
start = time.time()
import warnings
warnings.filterwarnings("ignore")




score_param = pd.read_csv("data/movie_reco_scores.csv", sep = ',')
refined_dataset = pd.read_csv("data/refined_dataset.csv")
refined_dataset = refined_dataset.loc[0:1000000,:]
refined_dataset = refined_dataset.drop('Unnamed: 0', axis='columns')

#user model
dataset_user = refined_dataset.loc[:, ['movieId', 'rating']] 

#Kmeans 15
kmeans_user_15 = KMeans(15)
kmeans_user_15.fit(dataset_user)
# Get the cluster labels
labels_15 = kmeans_user_15.labels_
# Calculate Davies-Bouldin and Calinski Harabasz scores
db_score_user_15 = davies_bouldin_score(dataset_user, labels_15)
db_score_user_15 = round(db_score_user_15, 2)
ch_score_user_15 = calinski_harabasz_score(dataset_user, labels_15)
ch_score_user_15 = round(ch_score_user_15, 2)

#Kmeans 25
kmeans_user_25 = KMeans(25)
kmeans_user_25.fit(dataset_user)
# Get the cluster labels
labels_25 = kmeans_user_25.labels_
# Calculate Davies-Bouldin and Calinski Harabasz scores
db_score_user_25 = davies_bouldin_score(dataset_user, labels_25)
db_score_user_25 = round(db_score_user_25, 2)
ch_score_user_25 = calinski_harabasz_score(dataset_user, labels_25)
ch_score_user_25 = round(ch_score_user_25, 2)

#Kmeans 35
kmeans_user_35 = KMeans(35)
kmeans_user_35.fit(dataset_user)
# Get the cluster labels
labels_35 = kmeans_user_35.labels_
# Calculate Davies-Bouldin and Calinski Harabasz scores
db_score_user_35 = davies_bouldin_score(dataset_user, labels_35)
db_score_user_35 = round(db_score_user_35, 2)
ch_score_user_35 = calinski_harabasz_score(dataset_user, labels_35)
ch_score_user_35 = round(ch_score_user_35, 2)

#Kmeans 45
kmeans_user_45 = KMeans(45)
kmeans_user_45.fit(dataset_user)
# Get the cluster labels
labels_45 = kmeans_user_45.labels_
# Calculate Davies-Bouldin and Calinski Harabasz scores
db_score_user_45 = davies_bouldin_score(dataset_user, labels_45)
db_score_user_45 = round(db_score_user_45, 2)
ch_score_user_45 = calinski_harabasz_score(dataset_user, labels_45)
ch_score_user_45 = round(ch_score_user_45, 2)

# Comparing Davies-Bouldin
db_score_user = [['db_score_user_15', db_score_user_15], ['db_score_user_25', db_score_user_25], ['db_score_user_35' , db_score_user_35], ['db_score_user_45', db_score_user_45]]
DB_score_user = pd.DataFrame(db_score_user, columns=['num_cluster_user', 'Davies-Bouldin_score'])
best_DB_score_user = DB_score_user.loc[DB_score_user['Davies-Bouldin_score'].idxmin()]
num_clus_user = int(best_DB_score_user.num_cluster_user[14:16])

#
kmeans_user = KMeans(num_clus_user)
identified_users= kmeans_user.fit_predict(dataset_user)
identified_users = list(identified_users)
refined_dataset['loc_clusters_users'] = identified_users

#movie model
dataset_movie = refined_dataset.loc[:, ['userId', 'rating']] 

#Kmeans 15
kmeans_movie_15 = KMeans(15)
kmeans_movie_15.fit(dataset_movie)
# Get the cluster labels
labels_15 = kmeans_movie_15.labels_
# Calculate Davies-Bouldin and Calinski Harabasz scores
db_score_movie_15 = davies_bouldin_score(dataset_movie, labels_15)
db_score_movie_15 = round(db_score_movie_15, 2)
ch_score_movie_15 = calinski_harabasz_score(dataset_movie, labels_15)
ch_score_movie_15 = round(ch_score_movie_15, 2)

#Kmeans 25
kmeans_movie_25 = KMeans(25)
kmeans_movie_25.fit(dataset_movie)
# Get the cluster labels
labels_25 = kmeans_movie_25.labels_
# Calculate Davies-Bouldin and Calinski Harabasz scores
db_score_movie_25 = davies_bouldin_score(dataset_movie, labels_25)
db_score_movie_25 = round(db_score_movie_25, 2)
ch_score_movie_25 = calinski_harabasz_score(dataset_movie, labels_25)
ch_score_movie_25 = round(ch_score_movie_25, 2)

#Kmeans 35
kmeans_movie_35 = KMeans(35)
kmeans_movie_35.fit(dataset_movie)
# Get the cluster labels
labels_35 = kmeans_movie_35.labels_
# Calculate Davies-Bouldin and Calinski Harabasz scores
db_score_movie_35 = davies_bouldin_score(dataset_movie, labels_35)
db_score_movie_35 = round(db_score_movie_35, 2)
ch_score_movie_35 = calinski_harabasz_score(dataset_movie, labels_35)
ch_score_movie_35 = round(ch_score_movie_35, 2)

#Kmeans 45
kmeans_movie_45 = KMeans(45)
kmeans_movie_45.fit(dataset_movie)
# Get the cluster labels
labels_45 = kmeans_movie_45.labels_
# Calculate Davies-Bouldin and Calinski Harabasz scores
db_score_movie_45 = davies_bouldin_score(dataset_movie, labels_45)
db_score_movie_45 = round(db_score_movie_45, 2)
ch_score_movie_45 = calinski_harabasz_score(dataset_movie, labels_45)
ch_score_movie_45 = round(ch_score_movie_45, 2)


db_score_movie = [['db_score_movie_15', db_score_movie_15], ['db_score_movie_25', db_score_movie_25], ['db_score_movie_35' , db_score_movie_35], ['db_score_movie_45', db_score_movie_45]]
 
# Create the pandas DataFrame
DB_score_movie = pd.DataFrame(db_score_movie, columns=['num_cluster_movie', 'Davies-Bouldin_score'])
best_DB_score_movie = DB_score_movie.loc[DB_score_movie['Davies-Bouldin_score'].idxmin()]
num_clus_movie = int(best_DB_score_movie.num_cluster_movie[15:17])

kmeans_movie = KMeans(num_clus_movie)
identified_movies = kmeans_movie.fit_predict(dataset_movie)
identified_movies = list(identified_movies)
refined_dataset['loc_clusters_movies'] = identified_movies

with open("models/kmeans_movie.pkl", "wb") as f:
    pickle.dump(kmeans_movie, f)
	
with open("models/kmeans_user.pkl", "wb") as f:
    pickle.dump(kmeans_user, f)
	
final_db = refined_dataset
final_db.to_pickle("data/final_db.pkl")
final_db.to_csv('data/final_db.csv', sep=',', encoding='utf-8', index=False)

num_users = final_db['userId'].nunique()

retrain = score_param['num_retraining'].max() + 1
end = time.time()
retrain_time = end - start
retrain_time = round(retrain_time)


new_score = pd.DataFrame({'num_retraining': retrain, 'retraining_time_seconds': retrain_time, 'num_users':num_users,  'db_score_reco_user_15': db_score_user_15, 'db_score_reco_user_25': db_score_user_25, 'db_score_reco_user_35': db_score_user_35, 'db_score_reco_user_45': db_score_user_45, 'db_score_reco_movie_15': db_score_movie_15, 'db_score_reco_movie_25': db_score_movie_25, 'db_score_reco_movie_35': db_score_movie_35, 'db_score_reco_movie_45': db_score_movie_45, 'ch_score_reco_user_15': ch_score_user_15, 'ch_score_reco_user_25': ch_score_user_25, 'ch_score_reco_user_35': ch_score_user_35, 'ch_score_reco_user_45': ch_score_user_45, 'ch_score_reco_movie_15': ch_score_movie_15, 'ch_score_reco_movie_25': ch_score_movie_25, 'ch_score_reco_movie_35': ch_score_movie_35, 'ch_score_reco_movie_45': ch_score_movie_45}, index=[0])

score_param = pd.concat([new_score,score_param.loc[:]])

score_param.to_csv('data/movie_reco_scores.csv', sep=',', encoding='utf-8', index=False)

print('Retrain done in :',retrain_time, 'seconds')