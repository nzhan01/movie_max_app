import logging
from sqlalchemy.exc import IntegrityError
from db import db
from datetime import datetime
from models.user_model import Users
from utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class Watchlist(db.Model):
    
    __tablename__ = 'watchlist'

    id = db.Column(db.Integer, primary_key=True)  # Added primary key for Watchlist
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, nullable = False) #Used to get movie info from TMDB
    movie_title = db.Column(db.String(200), nullable=False)
    overview = db.Column(db.Text, nullable = True)
    popularity = db.Column(db.Float, nullable=True)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    watched = db.Column(db.Boolean, default=False)

    user = db.relationship('Users', back_populates='watchlist')

    @staticmethod
    def add_to_watchlist(user_id, movie_id, title, overview=None, release_date=None, popularity=0.0):
        """
        Adds a movie to the user's watchlist.

        Args:
            user_id (int): ID of the user.
            movie_id (int): ID of the movie (from TMDB).
            title (str): Title of the movie.
            overview (str, optional): Overview/summary of the movie. Defaults to None.
            release_date (str, optional): Release date of the movie. Defaults to None.
            popularity (float, optional): Popularity score of the movie. Defaults to 0.0.

        Returns:
            None

        Raises:
            IntegrityError: If the movie cannot be added to the watchlist due to a database error.
        """
        entry = Watchlist(
            user_id=user_id,
            movie_id=movie_id,
            movie_title=title,
            overview=overview,
            release_date=release_date,
            popularity=popularity
        )
        db.session.add(entry)
        db.session.commit()

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
    
    
