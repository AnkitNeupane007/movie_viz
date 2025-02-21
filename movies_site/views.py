from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
import sqlite3
from .db import *
import random

views = Blueprint('views', __name__)

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
            
            return render_template('base.html', information=movie_information)
        else:
            flash('Movie not found', category='error')
            return redirect(url_for('views.home'))
    
    movie =  request.args.get('movie')
    
    if movie and check_movie(movie):
        movie_id = check_movie(movie)[0]
        movie_information = display_movie(movie_id)
        
        return render_template('base.html', information=movie_information)
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
                    
        return render_template('base.html', information=movie_information)
        
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
        if isinstance(actor_stats, dict):  # Check if it is dictionary
            return render_template('actors_and_directors.html', actor_stats=actor_stats)
        else:
            return render_template('actors_and_directors.html', actor_stats=None)
    
    return render_template('actors_and_directors.html', actor_stats=None)

@views.route('/fetch_director_stats', methods=['GET'])
def fetch_director_stats():
    director = request.args.get('director')
    
    if check_director(director):
        director = director.strip().title()
        director_stats = get_director_info(director)
        if isinstance(director_stats, dict):
            return render_template('actors_and_directors.html', director_stats=director_stats)
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
