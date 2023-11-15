# movie_recommendation_system_DS

Collaborative recommender system
--------------------------------
Collaborative filtering is based on the assumption that people who agreed in the past will agree in the future, and that they will like similar kinds of items as they liked in the past. The system generates recommendations using only information about rating profiles for different users or items. By locating peer users/items with a rating history similar to the current user or item, they generate recommendations using this neighborhood. This approach builds a model from a user’s past behaviors (items previously purchased or selected and/or numerical ratings given to those items) as well as similar decisions made by other users. This model is then used to predict items (or ratings for items) that the user may have an interest in. Collaborative filtering methods are classified as memory-based and model-based.

About DataSet
------------

•	Tags.csv ->
userId,movieId,tag,timestamp

•	movie.csv ->
movieId,title,genres

•	ratings.csv ->
userId, movieId, rating, timestamp

Environment Setp-up
-------------------

It is highly recommended setting up a virtual env following these steps:
1- Clone the repo
2- Inside of Anaconda terminal run the file create_venv_local.bat
3- This file will ask you the path of the venv (use the path of the folder of the proyect, this my path as example C:\Users\rafae\Desktop\MLOps\PF)
4- Activate your venv and you can start to work
