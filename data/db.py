import pandas as pd
import datetime

import sqlite3
connection = sqlite3.connect("movie.db")

from sqlalchemy import create_engine
engine = create_engine('sqlite:///movie.db', echo=False)

cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users_db(username, password)")

cursor.execute("INSERT INTO users_db VALUES ('admin', 'admin')")
cursor.execute("INSERT INTO users_db VALUES ('1', 'password')")

connection.commit()

cursor.execute("CREATE TABLE IF NOT EXISTS movies(movieId,title,genres)")
movies=pd.read_csv("./ml-latest-small/movies.csv")
movies.to_sql('movies', con=engine, if_exists='replace', index=False)

#
#
cursor.execute("CREATE TABLE IF NOT EXISTS ratings(userId,movieId,rating,timestamp)")
ratings = pd.read_csv("./ml-latest-small/ratings.csv")
ratings["timestamp"] = datetime.datetime.now()

ratings.to_sql('ratings', con=engine, if_exists='replace', index=False)
