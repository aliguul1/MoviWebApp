import os

import requests
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from data.data_manager import DataManager
from models import Movie, User, db

# Load environment variables
load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv('OMDB_API_KEY')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_key')

# Generic File Handling: Dynamic absolute path for SQLite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(DATA_DIR, 'moviweb.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
data_manager = DataManager()


# --- ERROR HANDLERS ---

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 Not Found errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 Internal Server errors."""
    return render_template('500.html'), 500


# --- ROUTES ---

@app.route('/')
def index():
    """Home page: Lists all users."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user entry."""
    name = request.form.get('name')
    if name:
        data_manager.create_user(name)
        flash(f"User '{name}' added successfully!")
    return redirect(url_for('index'))


@app.route('/users/<int:user_id>/movies')
def user_movies(user_id):
    """Display a specific user's movie collection."""
    user = User.query.get(user_id)
    if not user:
        return render_template('404.html'), 404
    return render_template('user_movies.html', user=user, movies=user.movies)


@app.route('/users/<int:user_id>/movies/add', methods=['POST'])
def add_movie(user_id):
    """Fetch OMDb data and add movie to the user's list."""
    title = request.form.get('title')
    url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if data.get('Response') == 'True':
            new_movie = Movie(
                title=data.get('Title'),
                director=data.get('Director'),
                year=data.get('Year'),
                poster_url=data.get('Poster'),
                user_id=user_id
            )
            data_manager.add_movie(new_movie)
            flash(f"'{new_movie.title}' added to favorites!")
        else:
            flash(f"OMDb Error: {data.get('Error')}")
    except Exception:
        flash("Connection error: Could not reach movie service.")
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Manually update the title of an existing movie."""
    movie = Movie.query.get(movie_id)
    if not movie:
        return render_template('404.html'), 404

    if request.method == 'POST':
        new_title = request.form.get('title')
        data_manager.update_movie(movie_id, new_title)
        flash("Movie title updated!")
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('update_movie.html', user=movie.user, movie=movie)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Delete a movie record."""
    data_manager.delete_movie(movie_id)
    flash("Movie removed.")
    return redirect(url_for('user_movies', user_id=user_id))


if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        db.create_all()
    app.run(debug=True)
