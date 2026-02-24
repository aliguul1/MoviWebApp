from sqlalchemy.exc import SQLAlchemyError
from models import Movie, User, db


class DataManager:
    """Handles all database CRUD operations."""

    def get_users(self):
        """Return all users."""
        return User.query.all()

    def create_user(self, name):
        """Add a user and commit to database."""
        try:
            new_user = User(name=name)
            db.session.add(new_user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()

    def add_movie(self, movie):
        """Add a movie and commit to database."""
        try:
            db.session.add(movie)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()

    def update_movie(self, movie_id, new_title):
        """Update a movie title and commit."""
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                movie.title = new_title
                db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()

    def delete_movie(self, movie_id):
        """Delete a movie and commit."""
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                db.session.delete(movie)
                db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()