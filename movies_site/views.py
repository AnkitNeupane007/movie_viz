from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
import sqlite3
from .db import *
import random
import requests

views = Blueprint('views', __name__)

def get_poster(movie_name):
    """Fetch the movie poster from OMDb API"""
    
    if not movie_name:
        return None  # Handle empty input

    url = f"https://www.omdbapi.com/?t={movie_name}&apikey={current_app.config.get('OMDB_API_KEY')}"
    
    try:
        response = requests.get(url, timeout=5).json()  # Set a timeout for API request
        
        if response.get("Response") == "True":
            return response.get("Poster")  # Return poster URL if found

    except requests.RequestException as e:
        current_app.logger.error(f"OMDb API request failed: {e}")  # Log errors

    return None  # Return None if poster is not found

def get_person_image(person_name):
    """Fetch an image of an actor or director using TMDb API."""
    
    if not person_name:
        return None

    # Construct the TMDb API URL with the query
    tmdb_url = f"https://api.themoviedb.org/3/search/person?query={person_name}&api_key={current_app.config.get('TMDB_API_KEY')}"

    try:
        # Request data from the API
        response = requests.get(tmdb_url, timeout=5).json()

        # Check if 'results' key exists and is non-empty
        if 'results' in response and response["results"]:
            # Get the profile image path from the first result
            profile_path = response["results"][0].get("profile_path")
            
            if profile_path:  # Ensure profile_path is not None or empty
                TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w185"
                return f"{TMDB_IMAGE_URL}{profile_path}"
            else:
                current_app.logger.warning(f"No profile image found for {person_name}.")
                return None
        else:
            current_app.logger.warning(f"No results found for {person_name}.")
            return None

    except requests.RequestException as e:
        current_app.logger.error(f"TMDb API request failed: {e}")
        return None



@views.route('/')
def home():
    return render_template('base.html')

@views.route('/about')
def about():
    return render_template('about.html')

@views.route('/search', methods=['GET', 'POST'])
def search_movie():
    
    if request.method == 'POST':
        movie = request.form.get('movie')
        
        if check_movie(movie):
            movie_id = check_movie(movie)[0]
            movie_information = display_movie(movie_id)
            movie_image = get_poster(movie)
            print(type(movie_image))
            
            return render_template('base.html', information=movie_information, movie_image=movie_image)
        else:
            flash('Movie not found', category='error')
            return redirect(url_for('views.home'))
    
    movie =  request.args.get('movie')
    
    if movie and check_movie(movie):
        movie_id = check_movie(movie)[0]
        movie_information = display_movie(movie_id)
        movie_image = get_poster(movie)
        
        return render_template('base.html', information=movie_information, movie_image=movie_image)
    else:
        flash('Movie not found', category='error')
        return redirect(url_for('views.home'))
    
    return redirect(url_for('views.home'))

@views.route('/api/suggestions', methods=['GET', 'POST'])
def search_suggestions_movies():
    
    prompt = request.args.get('query', '').strip().lower()
    if not prompt:
        return jsonify([])
        
    movies_list = search_movies(prompt)
    return jsonify(movies_list)

@views.route('/api/suggestions/actors', methods=['GET', 'POST'])
def search_suggestions_actors():
    
    prompt = request.args.get('query', '').strip().lower()
    if not prompt:
        return jsonify([])
    
    actors_list = search_actors(prompt)
    return jsonify(actors_list)

@views.route('/api/suggestions/directors', methods=['GET', 'POST'])
def search_suggestions_directors():
    
    prompt = request.args.get('query', '').strip().lower()
    if not prompt:
        return jsonify([])
    
    directors_list = search_directors(prompt)
    return jsonify(directors_list)

@views.route('/random', methods=['GET', 'POST'])
def random_movie():
    
    if request.method == 'POST':
        movie_id = random.randint(1, 2951)
        
        movie_information = display_movie(movie_id)
        movie_image = get_poster(movie_information['title'])
                    
        return render_template('base.html', information=movie_information, movie_image=movie_image)
        
    return redirect(url_for('views.home'))

@views.route('/visualize', methods=['GET', 'POST'])
def visualize():
    
    return render_template('visualizer.html')

@views.route('/actorsanddirectors', methods=['GET', 'POST'])
def actors_and_directors():
    
    return render_template('actors_and_directors.html')

@views.route('/api/get_rating_by_genre', methods=['GET'])
def get_rating_by_genre():
    genre = get_genres()
    genres = [g[0] for g in genre]
    rating_list = dict()
    
    for g in genres:
        rating = get_rating_per_genre(g)
        rating_list[g] = rating
        
    return jsonify(rating_list)


@views.route('/api/get_movies_by_genre', methods=['GET'])
def get_movies_by_genre():
    genre = request.args.get('genre')
    page = request.args.get('page', 1, type=int)
    limit = 10
    offset = (page - 1) * limit
    
    conn = get_db()
    db = conn.cursor()

    # Query to get movies of the selected genre, sorted by rating
    query = """
        SELECT m.title, m.release_date, m.runtime, m.tagline, m.overview, m.budget, 
               m.revenue, m.original_language, r.rating
        FROM movies m
        JOIN movie_genres mg ON m.id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.id
        LEFT JOIN reviews r ON m.id = r.movie_id
        WHERE g.name = ?
        ORDER BY r.rating DESC
        LIMIT ? OFFSET ?
    """
    db.execute(query, (genre, limit, offset))
    movies = db.fetchall()

    # Get the total number of movies for the genre to calculate total pages
    total_rows_query = """
        SELECT COUNT(DISTINCT m.id)
        FROM movies m
        JOIN movie_genres mg ON m.id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.id
        WHERE g.name = ?
    """
    total_rows = db.execute(total_rows_query, (genre,)).fetchone()[0]
    total_pages = (total_rows + limit - 1) // limit  # ceil division

    # Return the movies and pagination information as JSON
    return jsonify({
        'movies': [
            {
                'title': movie[0],
                'release_date': movie[1],
                'runtime': movie[2],
                'tagline': movie[3],
                'overview': movie[4],
                'budget': movie[5],
                'revenue': movie[6],
                'original_language': movie[7],
                'rating': movie[8]
            } for movie in movies
        ],
        'page': page,
        'total_pages': total_pages
    })


@views.route('/fetch_actor_stats', methods=['GET'])
def fetch_actor_stats():
    actor = request.args.get('actor')
    
    if check_actor(actor):
        actor = actor.strip().title()
        actor_stats = get_actor_info(actor)  # this return dictionary
        actor_image = get_person_image(actor)
        if isinstance(actor_stats, dict):  # Check if it is dictionary
            return render_template('actors_and_directors.html', actor_stats=actor_stats, actor_image=actor_image)
        else:
            return render_template('actors_and_directors.html', actor_stats=None)
    
    return render_template('actors_and_directors.html', actor_stats=None)

@views.route('/fetch_director_stats', methods=['GET'])
def fetch_director_stats():
    director = request.args.get('director')
    
    if check_director(director):
        director = director.strip().title()
        director_stats = get_director_info(director)
        director_image = get_person_image(director)
        if isinstance(director_stats, dict):
            return render_template('actors_and_directors.html', director_stats=director_stats, director_image=director_image)
        else:
            return render_template('actors_and_directors.html', director_stats=None)
                
    return render_template('actors_and_directors.html', director_stats=None)

@views.route('/compare_movies', methods=['GET'])
def compare_movies():
    movie1 = request.args.get('movie1')
    movie2 = request.args.get('movie2')

    if movie1 and movie2:
        # Check if movies exist in the database
        movie1_id = check_movie(movie1)
        movie2_id = check_movie(movie2)

        if movie1_id and movie2_id:
            # Fetch movie details using movie ids
            movie1_information = display_movie(movie1_id[0])
            movie2_information = display_movie(movie2_id[0])

            # Pass the movie details to the template for rendering
            return render_template('visualizer.html', movie_comparison={'movie1': movie1_information, 'movie2': movie2_information})
        else:
            flash('One or both movies not found', category='error')
            return redirect(url_for('views.visualize'))

    return redirect(url_for('views.visualize'))

@views.route('/api/top_grossing_movies', methods=['GET'])
def top_grossing_movies():
    movies = get_top_grossing_movies() # list of tuples (title, revenue)
    
    return jsonify(movies) if movies else jsonify([])

@views.route('/api/top_rated_movies', methods=['GET'])
def top_rated_movies():
    movies = get_top_rated_movies() # list of tuples (title, rating)
    
    return jsonify(movies) if movies else jsonify([])

@views.route('/api/top_movies_actors', methods=['GET'])
def top_movies_actors():
    actors = get_top_actors_most_movies() # list of tuples (director, no_of_movies)
    
    return jsonify(actors) if actors else jsonify([])

@views.route('/api/top_movies_directors', methods=['GET'])
def top_movies_directors():
    directors = get_top_directors_most_movies() # list of tuples (director, no_of_movies)
    
    return jsonify(directors) if directors else jsonify([])
    