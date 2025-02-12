from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from .db import *

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        stored_hashed_password = get_password(email)
        user_role = get_role(email)
        
        if stored_hashed_password is None:
            flash('No user with that email', category='error')
            return redirect(url_for('auth.login_user'))
        
        if check_password_hash(stored_hashed_password, password):
            
            session['user_id'] = email
            session['role'] = user_role
            
            if user_role == 'admin' and role == user_role:
                flash('Login Successfull', category='success')
                return redirect(url_for('admin.admin_dashboard'))
            elif user_role == 'reviewer' and role == user_role:
                flash('Login Successfull', category='success')
                return redirect(url_for('reviewer.reviewer_dashboard'))
            else:
                flash('You are of a different role', category='error')
        
        else:
            flash('Incorrect password', category='error')
            return redirect(url_for('auth.login_user'))
    
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup_user():
    if request.method == 'POST':
        role = request.form.get('role')
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        admin_count = check_admin()
        
        if admin_count >= 1 and role == 'admin':
            flash('Admin already exists', category='error')
            return redirect(url_for('auth.signup_user'))
        
        if len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(username) < 2:
            flash('Username must be greater than 2 characters', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        else:  
            hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')
            
            try:
                create_user(role, email, username, hashed_password)
            
                flash('Account created!', category='success')   
                return redirect(url_for('auth.login_user'))
            except sqlite3.Error as e:
                 flash(f"An error occurred: {e}", category='error')   
        
    return render_template('signup.html')

@auth.route('/logout')
def logout_user():
    # Remove user information from session
    session.pop('user_id', None)
    session.pop('role', None)
    
    flash('You have been logged out', category='success')
    return redirect(url_for('auth.login_user'))  # Redirect to login page
