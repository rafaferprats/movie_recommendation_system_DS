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

#uvicorn
#score_param = pd.read_csv("../data/movie_reco_scores.csv", sep = ',')
#refined_dataset = pd.read_csv("../data/refined_dataset.csv")


score_param = pd.read_csv("data/movie_reco_scores.csv", sep = ',')
refined_dataset = pd.read_csv("data/refined_dataset.csv")
refined_dataset = refined_dataset.loc[0:1000000,:]
refined_dataset = refined_dataset.drop('Unnamed: 0', axis='columns')

dataset_user = refined_dataset.loc[:, ['movieId', 'rating']] 
kmeans_user = KMeans(25)
kmeans_user.fit(dataset_user)

# Get the cluster labels
labels = kmeans_user.labels_

# Calculate Davies-Bouldin Index
db_score_reco_user = davies_bouldin_score(dataset_user, labels)
db_score_reco_user = round(db_score_reco_user, 2)

# Calculate silhouette score
#si_score = silhouette_score(dataset_user, labels)
#print("Silhouette score:", si_score)

ch_score_reco_user = calinski_harabasz_score(dataset_user, labels)
ch_score_reco_user = round(ch_score_reco_user, 2)

identified_users= kmeans_user.fit_predict(dataset_user)
identified_users = list(identified_users)
refined_dataset['loc_clusters_users'] = identified_users

dataset_movie = refined_dataset.loc[:, ['userId', 'rating']] 
kmeans_movie = KMeans(25)
kmeans_movie.fit(dataset_user)

# Get the cluster labels
labels = kmeans_movie.labels_

# Calculate Davies-Bouldin Index
db_score_reco_movie = davies_bouldin_score(dataset_movie, labels)
db_score_reco_movie = round(db_score_reco_movie, 2)

# Calculate silhouette score
#si_score = silhouette_score(dataset_movie, labels)
#print("Silhouette score:", si_score)

ch_score_reco_movie = calinski_harabasz_score(dataset_movie, labels)
ch_score_reco_movie = round(ch_score_reco_movie, 2)

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

retrain = score_param['retrain'].max() + 1
end = time.time()
retrain_time = end - start
retrain_time = round(retrain_time)

new_score = pd.DataFrame({'retrain': retrain, 'db_score_reco_user': db_score_reco_user, 'ch_score_reco_user': ch_score_reco_user, 'db_score_reco_movie': db_score_reco_movie, 'ch_score_reco_movie': ch_score_reco_movie,'retrain_time': retrain_time}, index=[0])
score_param = pd.concat([new_score,score_param.loc[:]])

score_param.to_csv('data/movie_reco_scores.csv', sep=',', encoding='utf-8', index=False)

print('Retrain done in :',retrain_time, 'seconds')