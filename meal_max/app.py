from dotenv import load_dotenv
import os
from flask import Flask, app, jsonify, make_response, Response, request
from werkzeug.exceptions import BadRequest, Unauthorized
import requests

from meal_max.utils.logger import configure_logger

# from flask_cors import CORS

"""test commeent  
dsf
dsf

dsf
"""
from meal_max.db import db
from meal_max.models import kitchen_model #Used as template
from meal_max.models.battle_model import BattleModel #Used as template
from meal_max.utils.sql_utils import check_database_connection, check_table_exists
from meal_max.models.mongo_session_model import login_user, logout_user 

from meal_max.models.user_model import Users
from meal_max.models.watchlist_model import Watchlist

# Load environment variables from .env file
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_READ_ACCESS_TOKEN = os.getenv("TMDB_READ_ACCESS_TOKEN")

app = Flask(__name__)
configure_logger(app.logger)


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///watchlist.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.init_app(app)  
    db.create_all()

#Ensures TMDB are loaded into the environment 
TMDB_READ_ACCESS_TOKEN = os.getenv("TMDB_READ_ACCESS_TOKEN")
BASE_URL = "https://api.themoviedb.org/3"

####################################################
#
# Root routes
#
####################################################
@app.route('/')
def root():
    return jsonify({"message": "Welcome to Movie Max"}), 200
@app.route('/api')
def api_root():
    return jsonify({"message": "Welcome to Movie Max API!"}), 200
####################################################
#
# Healthchecks
#
####################################################


@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)

@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection and users table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if meals table exists...")
        check_table_exists("meals")
        app.logger.info("meals table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)


@app.route('/api/create-user', methods=['POST'])
def create_user() -> Response:
        """
        Route to create a new user.

        Expected JSON Input:
            - username (str): The username for the new user.
            - password (str): The password for the new user.

        Returns:
            JSON response indicating the success of user creation.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the user to the database.
        """
        app.logger.info('Creating new user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return make_response(jsonify({'error': 'Invalid input, both username and password are required'}), 400)

            # Call the User function to add the user to the database
            app.logger.info('Adding user: %s', username)
            Users.create_user(username, password)

            app.logger.info("User added: %s", username)
            return make_response(jsonify({'status': 'user added', 'username': username}), 201)
        except Exception as e:
            app.logger.error("Failed to add user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/delete-user', methods=['DELETE'])
def delete_user() -> Response:
    """
    Route to delete a user.

    Expected JSON Input:
        - username (str): The username of the user to be deleted.

    Returns:
        JSON response indicating the success of user deletion.
    Raises:
        400 error if input validation fails.
        500 error if there is an issue deleting the user from the database.
    """
    app.logger.info('Deleting user')
    try:
        # Get the JSON data from the request
        data = request.get_json()

        # Extract and validate required fields
        username = data.get('username')

        if not username:
            return make_response(jsonify({'error': 'Invalid input, username is required'}), 400)

        # Call the User function to delete the user from the database
        app.logger.info('Deleting user: %s', username)
        Users.delete_user(username)

        app.logger.info("User deleted: %s", username)
        return make_response(jsonify({'status': 'user deleted', 'username': username}), 200)
    except Exception as e:
        app.logger.error("Failed to delete user: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/login', methods=['POST'])
def login():
    """
    Route to log in a user and load their combatants.

    Expected JSON Input:
        - username (str): The username of the user.
        - password (str): The user's password.

    Returns:
        JSON response indicating the success of the login.

    Raises:
        400 error if input validation fails.
        401 error if authentication fails (invalid username or password).
        500 error for any unexpected server-side issues.
    """
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        app.logger.error("Invalid request payload for login.")
        raise BadRequest("Invalid request payload. 'username' and 'password' are required.")

    username = data['username']
    password = data['password']

    try:
        # Validate user credentials
        if not Users.check_password(username, password):
            app.logger.warning("Login failed for username: %s", username)
            raise Unauthorized("Invalid username or password.")

        # Get user ID
        user_id = Users.get_id_by_username(username)

        # Load user's combatants into the battle model
        login_user(user_id, battle_model)

        app.logger.info("User %s logged in successfully.", username)
        return jsonify({"message": f"User {username} logged in successfully."}), 200

    except Unauthorized as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        app.logger.error("Error during login for username %s: %s", username, str(e))
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """
    Route to log out a user and save their combatants to MongoDB.

    Expected JSON Input:
        - username (str): The username of the user.

    Returns:
        JSON response indicating the success of the logout.

    Raises:
        400 error if input validation fails or user is not found in MongoDB.
        500 error for any unexpected server-side issues.
    """
    data = request.get_json()
    if not data or 'username' not in data:
        app.logger.error("Invalid request payload for logout.")
        raise BadRequest("Invalid request payload. 'username' is required.")

    username = data['username']

    try:
        # Get user ID
        user_id = Users.get_id_by_username(username)

        # Save user's combatants and clear the battle model
        logout_user(user_id, battle_model)

        app.logger.info("User %s logged out successfully.", username)
        return jsonify({"message": f"User {username} logged out successfully."}), 200

    except ValueError as e:
        app.logger.warning("Logout failed for username %s: %s", username, str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error("Error during logout for username %s: %s", username, str(e))
        return jsonify({"error": "An unexpected error occurred."}), 500

##########################################################

#
# API calls for getting movies
#
##########################################################


@app.route('/api/search-movie/<string:query>', methods=['GET'])
def search_movie(query):
    """
    Search for a movie using the TMDB API.

    Args:
        query (str): The search query for the movie.

    Returns:
        JSON response with movie search results or an error message.
    """
    if not TMDB_READ_ACCESS_TOKEN:  # Change: Validate API key existence
        app.logger.error("TMDB read access not found.")
        return jsonify({"error": "TMDB read access token not configured"}), 500

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
    try:
        response = requests.get(url, headers=headers, params=params)  # API request
        response.raise_for_status()  # Raise HTTP errors, if any
        data = response.json()

        # Filter the results to include only required fields
        filtered_results = [
            {
                "title": movie.get("title"),
                "release_date": movie.get("release_date"),
                "overview": movie.get("overview"),
                "vote_average": movie.get("vote_average")
            }
            for movie in data.get("results", [])
        ]

        # Return filtered results
        return jsonify(filtered_results)
    
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling TMDB API: {e}")
        return jsonify({"error": "Failed to fetch movie data"}), 500
    
@app.route('/api/movie/<int:movie_id>/providers', methods=['GET'])
def get_movie_providers(movie_id):
    # Construct the URL using the movie_id from the route
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"
    }

    # Send a GET request to the TMDB API
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # 'data' now contains all the watch provider information.
        # You can directly return this to the user, or filter it as needed.
        return jsonify(data), 200
    else:
        # If not successful, maybe the movie doesn't exist or TMDB is down.
        return jsonify({"error": "Failed to get watch providers"}), 500
    
@app.route('/api/movie/<int:movie_id>/recommendations', methods=['GET'])
def get_recommendations(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/recommendations"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # 'data["results"]' usually contains a list of recommended movies.
        recommendations = data.get("results", [])

        # For clarity, we might return a simplified list of recommended movies:
        simplified_recs = [
            {
                "title": rec.get("title"),
                "overview": rec.get("overview"),
                "release_date": rec.get("release_date"),
                "vote_average": rec.get("vote_average")
            }
            for rec in recommendations
        ]

        return jsonify(simplified_recs), 200
    else:
        return jsonify({"error": "Failed to get recommendations"}), 500



##########################################################
#
# Watch list
#
##########################################################
'''
@app.route('/add-to-watchlist', methods=['POST'])
def add_to_watchlist():
    data = request.json
    user_id = data['user_id']
    movie_id = data['movie_id']

    # Check if the movie is already in the watchlist
    existing_entry = Watchlist.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if existing_entry:
        return jsonify({"message": "Movie is already in your watchlist!"}), 400

    # Add the movie to the watchlist
    watchlist_entry = Watchlist(user_id=user_id, movie_id=movie_id)
    db.session.add(watchlist_entry)
    db.session.commit()

    return jsonify({"message": "Movie added to watchlist!"}), 201
'''


@app.route('/add-to-watchlist', methods=['POST'])
def add_to_watchlist():
    data = request.json
    user_id = data['user_id']
    movie_id = data['movie_id']

    # Validate if the movie exists on TMDB
    url = f"{BASE_URL}/movie/{movie_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return jsonify({"error": "Invalid movie ID"}), 400

    movie_data = response.json()

    # Check if the movie is already in the watchlist
    existing_entry = Watchlist.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if existing_entry:
        return jsonify({"message": "Movie is already in your watchlist!"}), 400

    # Add the movie to the watchlist
    watchlist_entry = Watchlist(
        user_id=user_id, 
        movie_id=movie_id, 
        title=movie_data.get('title'), 
        overview=movie_data.get('overview'),
        release_date=movie_data.get('release_date'), 
        vote_average=movie_data.get('vote_average'),
        popularity=movie_data.get('popularity', 0.0) )
        
    db.session.add(watchlist_entry)
    db.session.commit()

    return jsonify({"message": "Movie added to watchlist!"}), 201

'''
@app.route('/get-watchlist/<int:user_id>', methods=['GET'])
def get_watchlist(user_id):
    watchlist = Watchlist.query.filter_by(user_id=user_id).all()
    movie_details = []

    # Fetch movie details from the database or TMDB API
    for entry in watchlist:
        movie = Movies.query.filter_by(id=entry.movie_id).first()  # Or use TMDB API
        movie_details.append({
            "movie_id": entry.movie_id,
            "title": movie.title,
            "release_date": movie.release_date,
            "poster_path": movie.poster_path,
            "watched": entry.watched
        })

    return jsonify(movie_details), 200
'''

@app.route('/mark-watched', methods=['PUT'])
def mark_watched():
    data = request.json
    user_id = data['user_id']
    movie_id = data['movie_id']

    # Find the movie in the watchlist
    watchlist_entry = Watchlist.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if not watchlist_entry:
        return jsonify({"message": "Movie not found in watchlist!"}), 404

    # Mark it as watched
    watchlist_entry.watched = True
    db.session.commit()

    return jsonify({"message": "Movie marked as watched!"}), 200

@app.route('/remove-from-watchlist', methods=['DELETE'])
def remove_from_watchlist():
    data = request.json
    user_id = data['user_id']
    movie_id = data['movie_id']

    # Find the movie in the watchlist
    watchlist_entry = Watchlist.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if not watchlist_entry:
        return jsonify({"message": "Movie not found in watchlist!"}), 404

    # Remove it from the watchlist
    db.session.delete(watchlist_entry)
    db.session.commit()

    return jsonify({"message": "Movie removed from watchlist!"}), 200






if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)