import logging
from sqlalchemy.exc import IntegrityError
from db import db
from datetime import datetime
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


class Watchlist(db.Model):
    
    __tablename__ = 'watchlist'

    id = db.Column(db.Integer, primary_key=True)  # Added primary key for Watchlist
    movie_id = db.Column(db.Integer, nullable = False) #Used to get movie info from TMDB
    movie_title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('Users', back_populates='watchlist')

    
    def search_movie(query):
        """
        Search for a movie using the TMDB API.

        Args:
            query (str): The search query for the movie.

        Returns:
            List of filtered movie search results or an error message.
        """
        url = f"{BASE_URL}/search/movie"
        headers = {
            "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"  # Use the Read Access Token
        }
        params = {
            "query": query,
            "include_adult": "false",
            "language": "en-US",
            "page": 1
        }

        try:
            # Make the API request
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors

            data = response.json()

            # Filter the results to include only required fields
            filtered_results = [
                {
                    "title": movie.get("title"),
                    "id": movie.get("id")
                }
                for movie in data.get("results", [])
            ]

            return filtered_results

        except requests.exceptions.RequestException as e:
            print(f"Error with TMDB API call: {e}")
            return []
        

    @staticmethod
    def add_to_watchlist(username, movie_title):
        """
        Add a movie to the user's watchlist by searching TMDB and adding the movie's details to the database.
            

        Args:
            username (str): The username of the user adding the movie.
            movie_title (str): The title of the movie to be added.

        Returns:
            tuple: A tuple containing:
                - dict: JSON-compatible dictionary with a success message.
                - int: HTTP status code indicating success (200).

        Raises:
            ValueError: If the user is not found in the database.
            ValueError: If the movie title yields no results or an API error occurs.
            ValueError: If the movie is already in the user's watchlist.

        
        """
        user = Users.query.filter_by(username=username).first()
        if not user:
            raise ValueError(f"User '{username}' not found.")

        # Search for the movie in TMDB
        search_results = Watchlist.search_movie(movie_title)
        if not search_results:
            raise ValueError(f"Movie '{movie_title}' not found or API error.")

        # Get the first matching movie
        movie = search_results[0]

        # Check if the movie is already in the watchlist
        existing_entry = Watchlist.query.filter_by(user_id=user.id, movie_id=movie["id"]).first()
        if existing_entry:
            raise ValueError("Movie already in watchlist")

        # Add the movie to the watchlist
        new_entry = Watchlist(user_id=user.id, movie_title=movie["title"], movie_id=movie["id"])
        db.session.add(new_entry)
        db.session.commit()

        # Return a response tuple for compatibility with tests
        return {"message": f"'{movie['title']}' has been added to the watchlist"}, 200

    @staticmethod
    def get_watchlist(username: str) -> list:
        """
        Retrieves the watchlist for a given user.

        Args:
            username (str): The username of the user.

        Returns:
            list: A list of dictionaries containing watchlist entries with keys:
                  - "id": ID of the watchlist entry.
                  - "movie_title": Title of the movie.
                  - "added_on": Date and time the movie was added.
                  - "watched": Boolean indicating if the movie has been watched.

        Raises:
            ValueError: If the user is not found in the database.
        """
        user = Users.query.filter_by(username=username).first()
        if not user:
            logger.error("User '%s' not found.", username)
            raise ValueError(f"User '{username}' not found.")

        watchlist = Watchlist.query.filter_by(user_id=user.id).all()
        logger.info("Retrieved watchlist for user '%s'.", username)
        return [
            {"id": entry.id, "movie_id" : entry.movie_id, "movie_title": entry.movie_title, }
            for entry in watchlist
        ]

    @staticmethod
    def remove_from_watchlist(username, movie_title):
        """
        Remove a movie from the user's watchlist.

        Args:
            username (str): The username of the user removing the movie.
            movie_title (str): The title of the movie to be removed.

        Returns:
            tuple: A tuple containing:
                - dict: JSON-compatible dictionary with a success or error message.
                - int: HTTP status code indicating success (200) or failure (400).

        Raises:
            ValueError: If the user is not found in the database.
            ValueError: If the movie is not found in the user's watchlist.
        """
        # Retrieve the user
        user = Users.query.filter_by(username=username).first()
        if not user:
            raise ValueError(f"User '{username}' not found.")

        # Find the movie in the user's watchlist
        movie_entry = Watchlist.query.filter_by(user_id=user.id, movie_title=movie_title).first()
        if not movie_entry:
            raise ValueError(f"Movie '{movie_title}' not found in the user's watchlist.")

        # Remove the movie from the watchlist
        db.session.delete(movie_entry)
        db.session.commit()

        # Return a success message
        return {"message": f"'{movie_title}' has been removed from the watchlist"}, 200
