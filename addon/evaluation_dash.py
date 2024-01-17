import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

score_param = pd.read_csv("data/movie_reco_scores.csv", sep = ',')
score_param.head(10)
df = score_param.drop(score_param.index[len(score_param)-1])

figure = plt.figure(figsize=(8, 8), layout='constrained')
plt.subplot(3,2,1)
# Get current axis
ax = plt.gca()
figure.suptitle('Evaluation dashboard', fontsize=15)
 
# line plot for math marks
df.plot(kind='line',
        x='num_retraining',
        y='db_score_reco_user_15',
        color='green', ax=ax)

df.plot(marker = 'o',
        x='num_retraining',
        y='db_score_reco_user_25', linewidth = 2.5,
        color='red', ax=ax)
df.plot(kind='line',
        x='num_retraining',
        y='db_score_reco_user_35',
        color='darkviolet', ax=ax)
df.plot(kind='line',
        x='num_retraining',
        y='db_score_reco_user_45',
        color='blue', ax=ax)

plt.ylabel("Davies-Bouldin score", fontsize = 10)
plt.legend('',frameon=False)
ax.set_title("Model reco via user")

plt.subplot(3,2,2)
# Get current axis
ax = plt.gca()
 
# line plot for math marks
df.plot(kind='line',
        x='num_retraining',
        y='ch_score_reco_user_15',
        color='green', ax=ax)

df.plot(kind='line',
        x='num_retraining',
        y='ch_score_reco_user_25',
        color='red', ax=ax)
df.plot(kind='line',
        x='num_retraining',
        y='ch_score_reco_user_35',
        color='darkviolet', ax=ax)
df.plot(kind='line',
        x='num_retraining',
        y='ch_score_reco_user_45',
        color='blue', ax=ax)

plt.ylabel("Calinski–Harabasz score", fontsize = 10)
plt.legend( ('15 Cluster', '25 Cluster', '35 Cluster', '45 Cluster'))
ax.set_title("Model reco via user")

#movie
plt.subplot(3,2,3)
ax = plt.gca()
# line plot for math marks
df.plot(kind='line',
        x='num_retraining',
        y='db_score_reco_movie_15',
        color='green', ax=ax)

df.plot(marker = 'o',
        x='num_retraining',
        y='db_score_reco_movie_25', linewidth = 2.5,
        color='red', ax=ax)
df.plot(kind='line',
        x='num_retraining',
        y='db_score_reco_movie_35',
        color='darkviolet', ax=ax)
df.plot(kind='line',
        x='num_retraining',
        y='db_score_reco_movie_45',
        color='blue', ax=ax)

plt.ylabel("Davies-Bouldin score", fontsize = 10)
plt.legend('',frameon=False)
ax.set_title("Model reco via movie")

plt.subplot(3,2,4)
# Get current axis
ax = plt.gca()
 
# line plot for math marks
df.plot(kind='line',
        x='num_retraining',
        y='ch_score_reco_movie_15',
        color='green', ax=ax)

df.plot(kind='line',
        x='num_retraining',
        y='ch_score_reco_movie_25',
        color='red', ax=ax)
df.plot(kind='line',
        x='num_retraining',
        y='ch_score_reco_movie_35',
        color='darkviolet', ax=ax)
df.plot(kind='line',
        x='num_retraining',
        y='ch_score_reco_movie_45',
        color='blue', ax=ax)

plt.ylabel("Calinski–Harabasz score", fontsize = 10)
plt.legend( ('15 Cluster', '25 Cluster', '35 Cluster', '45 Cluster'))
ax.set_title("Model reco via movie")


plt.subplot(3,2,5)
c=plt.plot(df['num_retraining'], df['num_users'], '-o', linewidth = 2)
x=np.arange(1010,1050,8)
plt.yticks(x)
plt.xlabel("Numbers of retraining", fontsize = 10)
plt.ylabel("Numbers of Users", fontsize = 10)

plt.subplot(3,2,6)
c=plt.plot(df['num_retraining'], df['retraining_time_seconds'], '-o', linewidth = 2)
plt.xlabel("Numbers of retraining", fontsize = 10)
plt.ylabel("Retraining time (seconds)", fontsize = 10)
plt.savefig('data/Evaluation_dashboard.png')  