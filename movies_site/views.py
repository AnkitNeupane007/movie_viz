from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
import sqlite3
from .db import *

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
            movie_information = display_movie(movie_id)[0]
            
            return render_template('base.html', information=movie_information)
        else:
            flash('Movie not found', category='error')
            return redirect(url_for('views.home'))
    
    return redirect(url_for('views.home'))