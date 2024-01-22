import pandas as pd
import json

from main import get_movie_from_user
print(get_movie_from_user(1).to_json())

from main import get_movie_from_movie
print(get_movie_from_movie(4162).to_json())