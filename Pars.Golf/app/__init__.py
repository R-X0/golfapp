from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    
    from app.routes import main, auth, clubs, players, courses
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(clubs.bp)
    app.register_blueprint(players.bp)
    app.register_blueprint(courses.bp)
    
    return app

from app import models