from flask import Blueprint, render_template, request, flash, redirect, url_for
import sqlite3
from .db import *
from .decorators import *

reviewer = Blueprint('reviewer', __name__)

@reviewer.route('/')
@role_required('reviewer')
def reviewer_dashboard():
    return render_template('reviewer.html')

@reviewer.route('/update', methods=['GET', 'POST'])
@role_required('reviewer')
def update_movie():
    
    if request.method == 'POST':
        reviewer_rating = request.form.get('rating')
        movie = request.form.get('movie')
        
        if check_movie(movie):
            update_review(reviewer_rating, movie)
            flash('Review updated successfully', category='success')
            return redirect(url_for('reviewer.update_movie'))
        else:
            flash('No such movie', category='error')
            return redirect(url_for('reviewer.update_movie'))
    
    return render_template('reviewer.html')