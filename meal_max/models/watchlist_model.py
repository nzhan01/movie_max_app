import logging
from sqlalchemy.exc import IntegrityError
from meal_max.db import db
from datetime import datetime
from meal_max.models.user_model import Users
from meal_max.utils.logger import configure_logger
import os

from flask import Flask, app, jsonify, make_response, Response, request
import requests

logger = logging.getLogger(__name__)
configure_logger(logger)

TMDB_READ_ACCESS_TOKEN = os.getenv("TMDB_READ_ACCESS_TOKEN")
BASE_URL = "https://api.themoviedb.org/3"


class Watchlist(db.Model):
    
    __tablename__ = 'watchlist'

    id = db.Column(db.Integer, primary_key=True)  # Added primary key for Watchlist
    movie_id = db.Column(db.Integer, nullable = False) #Used to get movie info from TMDB
    movie_title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('Users', back_populates='watchlist')


    @staticmethod
    def add_to_watchlist(username, title):
        """
        Adds a movie to the user's watchlist by fetching its ID from the TMDB API.

        Args:
            username (str): Username of the user.
            title (str): Title of the movie.

        Returns:
            Response object indicating success or failure.
        """
        movie_title = title.strip()  # Strip extra spaces
        user = Users.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": f"User '{username}' not found"}), 404

        user_id = user.id

        # TMDB API call to search for the movie
        url = f'https://api.themoviedb.org/3/search/movie'
        params = {'api_key': TMDB_READ_ACCESS_TOKEN, 'query': movie_title}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Handle HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error with TMDB API call: {e}")
            return jsonify({"error": "Failed to fetch data from TMDB"}), 500

        # Debugging: Log the response
        try:
            response_data = response.json()
            print(f"Response JSON: {response_data}")  # Debugging log
        except ValueError as e:
            print(f"Invalid JSON response: {e}")
            return jsonify({"error": "Invalid response from TMDB"}), 500

        # Check for expected structure
        if not isinstance(response_data, dict) or "results" not in response_data:
            return jsonify({"error": "Unexpected response format from TMDB"}), 500

        # Extract results and check for matches
        search_results = response_data.get("results", [])
        print(f"Search Results: {search_results}")  # Debugging log

        if not search_results:
            return jsonify({"error": f"No results found for '{movie_title}'"}), 404

        # Use list comprehension to find a matching movie by title
        matching_movie = next(
            (result for result in search_results if result.get("title", "").lower() == movie_title.lower()), None
        )

        if matching_movie:
            movie_id = matching_movie.get("id")
            if movie_id:
                # Add to the watchlist
                try:
                    entry = Watchlist(
                        user_id=user_id,
                        movie_id=movie_id,
                        movie_title=matching_movie.get("title", movie_title),
                    )
                    db.session.add(entry)
                    db.session.commit()
                    return jsonify({"message": f"'{movie_title}' has been added to the watchlist"}), 200
                except Exception as e:
                    print(f"Database error: {e}")  # Debugging log
                    return jsonify({"error": str(e)}), 500

        return jsonify({"error": f"No exact match found for '{movie_title}'"}), 404

    '''
    @staticmethod
    def add_to_watchlist(username,title):
        """
        Adds a movie to the user's watchlist.

        Args:
            user_id (int): ID of the user.
            title (str): Title of the movie.
            
        Returns:
            None

        Raises:
            IntegrityError: If the movie cannot be added to the watchlist due to a database error.
        """


        
        movie_title = title
        user = Users.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": f"User '{username}' not found"}), 404

        user_id = user.id

        # TMDB API call to search for the movie
        url = f'https://api.themoviedb.org/3/search/movie'
        params = {'api_key': TMDB_READ_ACCESS_TOKEN, 'query': movie_title}

        response = requests.get(url, params=params)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data from TMDB"}), 500

        search_results = response.json().get('results', [])
        if not search_results:
            return jsonify({"error": f"No results found for '{movie_title}'"}), 404

        # Find the first result with the exact movie title
        for result in search_results:
            if result['title'].lower() == movie_title.lower():
                movie_id = result['id']
                

                # Add the movie to the watchlist
                try:
                    
                    entry = Watchlist(
                        user_id=user_id,
                        movie_id=movie_id,
                        movie_title=title,
                    )
                    db.session.add(entry)
                    db.session.commit()
                    return jsonify({"message": f"'{movie_title}' has been added to the watchlist"}), 200
                except Exception as e:
                    return jsonify({"error": str(e)}), 500

        # If no exact match is found
        return jsonify({"error": f"No exact match found for '{movie_title}'"}), 404
    '''       

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
            {"id": entry.id, "movie_title": entry.movie_title, "added_on": entry.added_on, "watched": entry.watched}
            for entry in watchlist
        ]

    @staticmethod
    def remove_from_watchlist(username: str, movie_title: str) -> dict:
        """
        Removes a movie from the user's watchlist.

        Args:
            username (str): The username of the user.
            movie_title (str): The title of the movie to be removed.

        Returns:
            dict: A message indicating the movie was removed, with the movie title.

        Raises:
            ValueError: If the user is not found or the movie is not in the user's watchlist.
        """
        user = Users.query.filter_by(username=username).first()
        if not user:
            logger.error("User '%s' not found.", username)
            raise ValueError(f"User '{username}' not found.")

        entry = Watchlist.query.filter_by(user_id=user.id, movie_title=movie_title).first()
        if not entry:
            logger.error("Movie '%s' not found in %s's watchlist.", movie_title, username)
            raise ValueError(f"Movie '{movie_title}' not found in the watchlist.")

        db.session.delete(entry)
        db.session.commit()
        logger.info("Movie '%s' removed from %s's watchlist.", movie_title, username)
        return {"message": "Movie removed from watchlist", "movie_title": movie_title}
    
    
