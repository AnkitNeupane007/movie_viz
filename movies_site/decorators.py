from functools import wraps
from flask import session, redirect, url_for, flash
import sqlite3

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('You must be logged in to access this page.', 'error')
                return redirect(url_for('auth.login_user'))
            
            # Query the user's role from the database
            conn = sqlite3.connect('instance/movies.db')
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE email = ?", (session['user_id'],))
            user_role = cursor.fetchone()
            conn.close()

            if user_role is None or user_role[0] != role:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('views.home'))  # Or any other page you'd like to redirect to

            return f(*args, **kwargs)
        return decorated_function
    return decorator
