from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from time import time
import jwt
from flask import current_app
import re

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    profile_image = db.Column(db.String(120), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.Text)
    oauth_provider = db.Column(db.String(20))
    oauth_id = db.Column(db.String(100))
    
    # Relationships
    clubs_submitted = db.relationship('Club', backref='submitter', lazy='dynamic', 
                                     foreign_keys='Club.submitter_id')
    players_submitted = db.relationship('Player', backref='submitter', lazy='dynamic',
                                       foreign_keys='Player.submitter_id')
    courses_submitted = db.relationship('Course', backref='submitter', lazy='dynamic',
                                       foreign_keys='Course.submitter_id')
    votes = db.relationship('Vote', backref='user', lazy='dynamic',
                           foreign_keys='Vote.user_id')
    player_profile = db.relationship('Player', backref='player_user', uselist=False,
                                    primaryjoin="User.id==Player.user_id", overlaps="players_submitted")
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['reset_password']
            return User.query.get(id)
        except:
            return None
    
    @property
    def formatted_username(self):
        return f'pars.golf/@{self.username}'
    
    @staticmethod
    def validate_username(username):
        return re.match(r'^[a-zA-Z0-9_]+$', username) is not None
    
    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))