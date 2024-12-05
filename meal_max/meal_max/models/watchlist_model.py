import json
import logging
from sqlalchemy.exc import IntegrityError
from db import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from user_model import Users
from utils import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class WatchlistManager(db.Model):


    __tablename__ = 'watchlist'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    watched = db.Column(db.Boolean, default=False)

    #def __repr__(self):
       # return f'<Watchlist {self.user_id} - {self.movie_id}>'

    @staticmethod
    def add_to_watchlist(username: str, movie: dict) -> None:
        user = Users.query.filter_by(username=username).first()
        if not user:
            logger.error("User '%s' not found.", username)
            raise ValueError(f"User '{username}' not found.")

        # Parse the current watchlist
        current_watchlist = json.loads(user.watchlist) if user.watchlist else []

        # Check for duplicate movie
        if any(existing_movie['title'] == movie['title'] for existing_movie in current_watchlist):
            logger.error("Movie '%s' already exists in %s's watchlist.", movie['title'], username)
            raise ValueError(f"Movie '{movie['title']}' already exists in the watchlist.")

        # Add the new movie and update the watchlist
        current_watchlist.append(movie)
        user.watchlist = json.dumps(current_watchlist)
        db.session.commit()
        logger.info("Movie '%s' added to %s's watchlist.", movie['title'], username)

    @staticmethod
    def view_watchlist(username: str) -> list:
        user = Users.query.filter_by(username=username).first()
        if not user:
            logger.error("User '%s' not found.", username)
            raise ValueError(f"User '{username}' not found.")

        # Return the watchlist or an empty list
        return json.loads(user.watchlist) if user.watchlist else []

    @staticmethod
    def remove_from_watchlist(username: str, movie_title: str) -> None:
        user = Users.query.filter_by(username=username).first()
        if not user:
            logger.error("User '%s' not found.", username)
            raise ValueError(f"User '{username}' not found.")

        # Parse the current watchlist
        current_watchlist = json.loads(user.watchlist) if user.watchlist else []

        # Check if the movie exists
        updated_watchlist = [movie for movie in current_watchlist if movie['title'] != movie_title]
        if len(updated_watchlist) == len(current_watchlist):
            logger.error("Movie '%s' not found in %s's watchlist.", movie_title, username)
            raise ValueError(f"Movie '{movie_title}' not found in the watchlist.")

        # Update the watchlist
        user.watchlist = json.dumps(updated_watchlist) if updated_watchlist else None
        db.session.commit()
        logger.info("Movie '%s' removed from %s's watchlist.", movie_title, username)
