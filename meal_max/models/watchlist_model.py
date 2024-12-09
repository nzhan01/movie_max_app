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

    id = db.Column(db.Integer, primary_key=True)
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
    
    
