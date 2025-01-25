''' __init__.py banayo bhane yo purai folder lai as a package treat garna milcha '''

from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ezgg'
    app.config['DATABASE'] = 'instance/movies.db'
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