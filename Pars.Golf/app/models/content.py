from app import db
from datetime import datetime

class Club(db.Model):
    __tablename__ = 'clubs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    brand = db.Column(db.String(100), index=True)
    club_type = db.Column(db.String(50), index=True)  # driver, iron, putter, etc.
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    purchase_link = db.Column(db.String(255))
    price = db.Column(db.Float)
    release_year = db.Column(db.Integer)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    votes = db.relationship('Vote', backref='club', lazy='dynamic',
                          primaryjoin="and_(Vote.club_id==Club.id, Vote.content_type=='club')",
                          foreign_keys="Vote.club_id")
    
    @property
    def vote_count(self):
        return self.votes.count()
    
    def __repr__(self):
        return f'<Club {self.brand} {self.name}>'

class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.Text)
    country = db.Column(db.String(100))
    world_ranking = db.Column(db.Integer)
    pro_since = db.Column(db.Integer)
    major_wins = db.Column(db.Integer, default=0)
    tour_wins = db.Column(db.Integer, default=0)
    verified = db.Column(db.Boolean, default=False)
    approved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # If player has account
    user_account = db.relationship('User', foreign_keys=[user_id], overlaps="players_submitted")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    votes = db.relationship('Vote', backref='player', lazy='dynamic',
                          primaryjoin="and_(Vote.player_id==Player.id, Vote.content_type=='player')",
                          foreign_keys="Vote.player_id")
    
    @property
    def vote_count(self):
        return self.votes.count()
    
    def __repr__(self):
        return f'<Player {self.name}>'

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    website = db.Column(db.String(255))
    par = db.Column(db.Integer)
    length_yards = db.Column(db.Integer)
    difficulty_rating = db.Column(db.Float)
    year_built = db.Column(db.Integer)
    designer = db.Column(db.String(100))
    is_public = db.Column(db.Boolean, default=True)
    has_hosted_major = db.Column(db.Boolean, default=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    votes = db.relationship('Vote', backref='course', lazy='dynamic',
                          primaryjoin="and_(Vote.course_id==Course.id, Vote.content_type=='course')",
                          foreign_keys="Vote.course_id")
    
    @property
    def vote_count(self):
        return self.votes.count()
    
    def __repr__(self):
        return f'<Course {self.name}>'

class Vote(db.Model):
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    content_type = db.Column(db.String(20))  # 'club', 'player', or 'course'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'club_id', 'content_type', name='uq_vote_club'),
        db.UniqueConstraint('user_id', 'player_id', 'content_type', name='uq_vote_player'),
        db.UniqueConstraint('user_id', 'course_id', 'content_type', name='uq_vote_course'),
    )
    
    def __repr__(self):
        return f'<Vote {self.id}>'