import os
import pandas as pd
from d2l import mxnet as d2l

from sqlalchemy import create_engine
import mysql.connector
import datetime

# Replace these with your actual database credentials
user = 'root'
password = 'password'
host = 'localhost'
database = 'movie'

# Create the MySQL engine
engine = create_engine(f'mysql://{user}:{password}@{host}/{database}')

connection = mysql.connector.connect(host='localhost',
                                         database='movie',
                                         user='root',
                                         password='password')
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS  users_db(
username VARCHAR(255) not null, 
password VARCHAR(255) not null);""")

cursor.execute("INSERT INTO users_db VALUES ('admin', 'admin')")
cursor.execute("INSERT INTO users_db VALUES ('1', 'password')")

connection.commit()


#@save
d2l.DATA_HUB['ml-100k'] = (
    'https://files.grouplens.org/datasets/movielens/ml-100k.zip',
    'cd4dcac4241c8a4ad7badc7ca635da8a69dddb83')

#@save
def read_data_ml100k():
    data_dir = d2l.download_extract('ml-100k')
    names = ['user_id', 'item_id', 'rating', 'timestamp']
    data = pd.read_csv(os.path.join(data_dir, 'u.data'), sep='\t',
                       names=names, engine='python')
    names_ = ['movieId', 'title', 'genre', "release date" , "video release date" ,
              "IMDb URL" , "unknown" ,"Action" , "Adventure" , "Animation" ,
              "Children's" , "Comedy" , "Crime" , "Documentary" , "Drama" , "Fantasy" ,
              "Film-Noir" , "Horror" , "Musical" , "Mystery" , "Romance" , "Sci-Fi" ,
              "Thriller" , "War" , "Western" ]
    data_movie = pd.read_csv(os.path.join(data_dir, 'u.item'), sep='|',encoding="ISO-8859-1",
                       names=names_, engine='python')
    num_users = data.user_id.unique().shape[0]
    num_items = data.item_id.unique().shape[0]
    return data,data_movie, num_users, num_items

data,data_movie, num_users, num_items = read_data_ml100k()
sparsity = 1 - len(data) / (num_users * num_items)
print(f'number of users: {num_users}, number of items: {num_items}')
print(f'matrix sparsity: {sparsity:f}')
data["timestamp"] = datetime.datetime.now()
# print(data.head(5))

# data.to_sql('ratings', con=engine, if_exists='replace', index=False)
data_movie = data_movie[['movieId', 'title']]
# print(data_movie.head())
data_movie.to_sql('movies', con=engine, if_exists='replace', index=False)

