import os
from dotenv import load_dotenv



load_dotenv()
TMDB_READ_ACCESS_TOKEN = os.getenv("TMDB_READ_ACCESS_TOKEN")

import requests

url = "https://api.themoviedb.org/3/search/movie"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer " +TMDB_READ_ACCESS_TOKEN
}
params = {
    "query": "Inception",
    "include_adult": "false",
    "language": "en-US",
    "page": 1
}

response = requests.get(url, headers=headers, params=params)
print(response.status_code)
print(response.json())

#print(TMDB_READ_ACCESS_TOKEN)