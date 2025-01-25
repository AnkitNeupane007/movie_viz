from flask import Blueprint, render_template, request, flash, redirect, url_for
import sqlite3
from .db import *
from .decorators import *

admin = Blueprint('admin', __name__)

@admin.route('/')
@role_required('admin')
def admin_dashboard():
    return render_template('<p>This is admin</>')