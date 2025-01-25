from flask import Blueprint, jsonify, render_template, request
import sqlite3

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('base.html')

@views.route('/about')
def about():
    return render_template('about.html')