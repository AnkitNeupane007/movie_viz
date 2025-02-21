''' __init__.py banayo bhane yo purai folder lai as a package treat garna milcha '''

from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['DATABASE'] = os.getenv('DATABASE_URL')
    app.config['DEBUG'] = True
    # Kun route ma jaani register garna lai
    from .views import views
    from .auth import auth
    from .reviewer import reviewer
    from .admin import admin 
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(reviewer, url_prefix='/reviewer')
    app.register_blueprint(admin, url_prefix='/admin')

    
    
    return app