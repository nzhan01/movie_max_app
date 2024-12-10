import logging
from sqlalchemy.exc import IntegrityError
from db import db
from models.user_model import Users
from utils.logger import configure_logger
import os
from dotenv import load_dotenv

from flask import Flask, app, jsonify, make_response, Response, request
import requests

logger = logging.getLogger(__name__)
configure_logger(logger)
load_dotenv()
TMDB_READ_ACCESS_TOKEN = os.getenv("TMDB_READ_ACCESS_TOKEN")
BASE_URL = "https://api.themoviedb.org/3"


class Movie():
    def search_movie(query):
        """Search for a movie using the TMDB API."""
        url = f"{BASE_URL}/search/movie"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"
        }
        params = {
            "query": query,
            "include_adult": "false",
            "language": "en-US",
            "page": 1
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return [
            {
                "title": movie.get("title"),
                "movie_id": movie.get("id"),
                "release_date": movie.get("release_date"),
                "overview": movie.get("overview"),
                "vote_average": movie.get("vote_average")
            }
            for movie in data.get("results", [])
        ]

    def get_movie_providers(movie_id):
        """Get watch providers for a specific movie."""
        url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_recommendations(movie_id):
        """Get recommendations for a specific movie."""
        url = f"{BASE_URL}/movie/{movie_id}/recommendations"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return [
            {
                "title": rec.get("title"),
                "overview": rec.get("overview"),
                "release_date": rec.get("release_date"),
                "vote_average": rec.get("vote_average")
            }
            for rec in data.get("results", [])
        ]

    def get_movie_details(movie_id):
        """Fetch detailed information about a specific movie."""
        url = f"{BASE_URL}/movie/{movie_id}"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return {
            "id": data.get("id"),
            "title": data.get("title"),
            "overview": data.get("overview"),
            "release_date": data.get("release_date"),
            "vote_average": data.get("vote_average"),
            "vote_count": data.get("vote_count"),
            "popularity": data.get("popularity"),
            "runtime": data.get("runtime"),
            "genres": [genre["name"] for genre in data.get("genres", [])]
        }

    def get_popular_movies():
        """Fetch the current popular movies."""
        url = f"{BASE_URL}/movie/popular"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
