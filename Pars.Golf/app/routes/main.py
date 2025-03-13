from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.content import Club, Player, Course, Vote
from app.models.user import User, Role
from sqlalchemy import and_
from werkzeug.utils import secure_filename
import os
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # For first run, just return empty lists if tables don't exist yet
    try:
        # Simple query to check if tables exist
        db.session.execute(db.select(Club.id).limit(1))
        db.session.execute(db.select(Player.id).limit(1))
        db.session.execute(db.select(Course.id).limit(1))
        
        # If tables exist, get the data
        top_clubs = Club.query.filter_by(approved=True).limit(5).all()
        top_players = Player.query.filter_by(approved=True).limit(5).all()
        top_courses = Course.query.filter_by(approved=True).limit(5).all()
    except Exception as e:
        # For first run without tables
        print(f"Database tables not ready: {e}")
        top_clubs = []
        top_players = []
        top_courses = []
    
    return render_template('index.html', 
                          title='Par-Fect Your Game',
                          top_clubs=top_clubs,
                          top_players=top_players,
                          top_courses=top_courses)

@bp.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    clubs_submitted = Club.query.filter_by(submitter=user, approved=True).all()
    players_submitted = Player.query.filter_by(submitter=user, approved=True).all()
    courses_submitted = Course.query.filter_by(submitter=user, approved=True).all()
    
    club_votes = Vote.query.filter_by(user=user, content_type='club').all()
    player_votes = Vote.query.filter_by(user=user, content_type='player').all()
    course_votes = Vote.query.filter_by(user=user, content_type='course').all()
    
    return render_template('profile.html', 
                           title=f'Profile - {user.username}',
                           user=user,
                           clubs_submitted=clubs_submitted,
                           players_submitted=players_submitted,
                           courses_submitted=courses_submitted,
                           club_votes=club_votes,
                           player_votes=player_votes,
                           course_votes=course_votes)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    from app.utils.forms import EditProfileForm
    
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.profile_image.data:
            filename = secure_filename(form.profile_image.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            form.profile_image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            current_user.profile_image = filename
        
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.profile', username=current_user.username))
    
    elif request.method == 'GET':
        form.bio.data = current_user.bio
    
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@bp.route('/admin')
@login_required
def admin_dashboard():
    # Check if user is admin
    if current_user.role.name != 'Admin':
        flash('You do not have permission to access the admin dashboard.')
        return redirect(url_for('main.index'))
    
    pending_clubs = Club.query.filter_by(approved=False).all()
    pending_players = Player.query.filter_by(approved=False).all()
    pending_courses = Course.query.filter_by(approved=False).all()
    
    users = User.query.all()
    roles = Role.query.all()
    
    return render_template('admin/dashboard.html', 
                           title='Admin Dashboard',
                           pending_clubs=pending_clubs,
                           pending_players=pending_players,
                           pending_courses=pending_courses,
                           users=users,
                           roles=roles)

@bp.route('/employee')
@login_required
def employee_dashboard():
    # Check if user is employee
    if current_user.role.name not in ['Employee', 'Admin']:
        flash('You do not have permission to access the employee dashboard.')
        return redirect(url_for('main.index'))
    
    pending_clubs = Club.query.filter_by(approved=False).all()
    pending_players = Player.query.filter_by(approved=False).all()
    pending_courses = Course.query.filter_by(approved=False).all()
    
    return render_template('employee/dashboard.html', 
                           title='Content Moderation',
                           pending_clubs=pending_clubs,
                           pending_players=pending_players,
                           pending_courses=pending_courses)