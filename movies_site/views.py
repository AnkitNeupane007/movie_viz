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
    if request.method == 'POST':
        pass
    
    return render_template('visualizer.html')

def get_actor_stats(actor):
    
    return "actor_stats"

def get_director_stats(director):
    
    return "director_stats"

@views.route('/fetch_actor_stats', methods=['GET'])
def fetch_actor_stats():
    actor = request.args.get('actor')
    if actor:
        actor_stats = get_actor_stats(actor)
        
        return render_template('visualizer.html', actor_stats=actor_stats)

    return render_template('visualizer.html', actor_stats=None)

@views.route('/fetch_director_stats', methods=['GET'])
def fetch_director_stats():
    director = request.args.get('director')
    
    if director:
        director_stats = get_director_stats(director)
            
        return render_template('visualizer.html', director_stats=director_stats)
    
    return render_template('visualizer.html', director_stats=None)

@views.route('/compare_movies', methods=['GET', 'POST'])
def compare_movies():
    if request.method == 'POST':
        movie1 = request.form.get('movie1')
        movie2 = request.form.get('movie2')
        
        movie1_id = check_movie(movie1)
        movie2_id = check_movie(movie2)
        
        if movie1_id and movie2_id:
            movie1_information = display_movie(movie1_id[0])
            movie2_information = display_movie(movie2_id[0])
            
            return render_template('base.html', movie1=movie1_information, movie2=movie2_information)
        else:
            flash('Movie not found', category='error')
            return redirect(url_for('views.visualize'))
    
    return redirect(url_for('views.visualize'))