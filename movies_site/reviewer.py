from flask import Blueprint, render_template, request, flash, redirect, url_for
import sqlite3
from .db import *
from .decorators import *

reviewer = Blueprint('reviewer', __name__)

@reviewer.route('/')
@role_required('reviewer')
def reviewer_dashboard():
    return render_template('reviewer.html')