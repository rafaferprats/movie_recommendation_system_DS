# movie_recommendation_system_DS

Collaborative recommender system
--------------------------------
Collaborative filtering is based on the assumption that people who agreed in the past will agree in the future, and that they will like similar kinds of items as they liked in the past. The system generates recommendations using only information about rating profiles for different users or items. By locating peer users/items with a rating history similar to the current user or item, they generate recommendations using this neighborhood. This approach builds a model from a user’s past behaviors (items previously purchased or selected and/or numerical ratings given to those items) as well as similar decisions made by other users. This model is then used to predict items (or ratings for items) that the user may have an interest in. Collaborative filtering methods are classified as memory-based and model-based.

Success Criteria
--------------------------------
Success will be measured by implementing collaborative and content-based models that can return movie recommendations to a user. The goal is to provide reviews that we find sensible based on either reviews that the user enters, or based on a film given to the content-based system. A good recommendation algorithm can be extremely useful for streaming companies, as a constant stream of accurate or interesting recommendations will keep users engaged with the platform.

Members
--------------------------------
|         Name             
|--------------------------
|Rafael Fernandez        
|Guilherme Santos       
|Claudia Clörs          

About DataSet
------------

•	Tags.csv ->
userId,movieId,tag,timestamp

•	movie.csv ->
movieId,title,genres

•	ratings.csv ->
userId, movieId, rating, timestamp

Environment Set-up
-------------------

It is highly recommended setting up a virtual env following these steps:

1- Clone the repo

2- Inside of Anaconda terminal navigate to the folder bin/local/ and  run the file create_venv_local.bat

3- This file will ask you the path of the venv (use the path of the folder of the proyect, this is my path as example C:\Users\rafae\Desktop\MLOps\PF) and create the venv following the python version defined at the environment.yml with the proper requirements.txt

4- Activate your venv and you can start to work


API Set-up
-------------------
start the API via the command
```uvicorn main:app --reload```

API call example
-------------------
via userId:
userID=1

```curl -X 'GET' \
  'http://127.0.0.1:8000/movie_recommendation_via_user/{userId}?input_user=1' \
  -H 'accept: application/json'
  ```

```http://127.0.0.1:8000/movie_recommendation_via_user/{userId}?input_user=1```

via movieId:
movieId = 994

```curl -X 'GET' \
  'http://127.0.0.1:8000/movie_recomendation_via_movie/{movieId}?input_movie=994' \
  -H 'accept: application/json'
```
```http://127.0.0.1:8000/movie_recomendation_via_movie/{movieId}?input_movie=994```


API v2 Set-up (main.py)
-------------------
start the API via Anaconda prompt
```python main.py```

API v2 call example (main.py)
-------------------
via userId:
userID=3467

```http://127.0.0.1:5500/movie_recommendation_via_user/{userId}?input_user=100```

via movieId:
movieId = 994


```http://127.0.0.1:5500/movie_recomendation_via_movie/{movieId}?input_movie=3467```

