from flask import Blueprint, render_template, request, flash, redirect, url_for
import sqlite3
from .db import *
from .decorators import *

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@role_required('admin')
def admin_dashboard():
    
    # display the list of all the users
    users = get_all_users()
    
    return render_template('admin.html', users=users)

@admin.route('/delete_user', methods=['GET'])
@role_required('admin')
def delete_user():
    
    email = request.args.get('user_email')
    
    if email:
        delete_user_from_database(email)
        flash('User deleted successfully', category='success')
    else:
        flash('No user to delete', category='error')
        
    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/update_user', methods=['GET', 'POST'])
@role_required('admin')
def update_user():
    
    email = request.form.get('user_email')
    new_username = request.form.get('new_username')
    
    # print(email, new_username)
    
    if email:
        update_user_in_database(email, new_username)
        flash('User updated successfully', category='success')
    else:
        flash('No user to update', category='error')
        
    return redirect(url_for('admin.admin_dashboard'))