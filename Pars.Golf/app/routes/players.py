from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.content import Player, Vote
from app.models.user import User
from app.utils.forms import PlayerForm
from werkzeug.utils import secure_filename
import os
import csv
import io
from datetime import datetime

bp = Blueprint('players', __name__, url_prefix='/players')

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'votes')
    filter_country = request.args.get('country')
    
    query = Player.query.filter_by(approved=True)
    
    if filter_country:
        query = query.filter_by(country=filter_country)
    
    if sort_by == 'votes':
        players = query.join(Vote, Player.id == Vote.player_id)\
            .group_by(Player.id)\
            .order_by(db.func.count(Vote.id).desc())\
            .paginate(page=page, per_page=12)
    elif sort_by == 'ranking':
        players = query.order_by(Player.world_ranking).paginate(page=page, per_page=12)
    elif sort_by == 'name':
        players = query.order_by(Player.name).paginate(page=page, per_page=12)
    else:
        players = query.join(Vote, Player.id == Vote.player_id)\
            .group_by(Player.id)\
            .order_by(db.func.count(Vote.id).desc())\
            .paginate(page=page, per_page=12)
    
    # Get unique countries for filtering
    countries = db.session.query(Player.country).distinct().all()
    
    return render_template('players/index.html', 
                           title='Golf Players',
                           players=players,
                           countries=[country[0] for country in countries],
                           current_sort=sort_by,
                           current_country=filter_country)

@bp.route('/<int:id>')
def show(id):
    player = Player.query.filter_by(id=id, approved=True).first_or_404()
    
    # Check if current user has voted for this player
    user_voted = False
    if current_user.is_authenticated:
        vote = Vote.query.filter_by(
            user_id=current_user.id,
            player_id=player.id,
            content_type='player'
        ).first()
        user_voted = vote is not None
    
    # Get associated user if this is a verified player
    user_account = player.user_account if player.user_id else None
    
    return render_template('players/show.html', 
                           title=player.name,
                           player=player,
                           user_voted=user_voted,
                           user_account=user_account)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = PlayerForm()
    if form.validate_on_submit():
        # Handle image upload
        image_url = None
        if form.profile_image.data:
            filename = secure_filename(form.profile_image.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            form.profile_image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'players', filename))
            image_url = f'/static/uploads/players/{filename}'
        
        # Create player
        player = Player(
            name=form.name.data,
            profile_image=image_url,
            bio=form.bio.data,
            country=form.country.data,
            world_ranking=form.world_ranking.data,
            pro_since=form.pro_since.data,
            major_wins=form.major_wins.data,
            tour_wins=form.tour_wins.data,
            submitter=current_user,
            # Set approved to True if user is Employee or Admin
            approved=current_user.role.name in ['Employee', 'Admin']
        )
        
        db.session.add(player)
        db.session.commit()
        
        flash('Your player has been submitted for approval!' if not player.approved else 'Player added successfully!')
        return redirect(url_for('players.show', id=player.id))
    
    return render_template('players/new.html', title='Add Player', form=form)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    player = Player.query.get_or_404(id)
    
    # Check if user is submitter, employee or admin
    if player.submitter != current_user and current_user.role.name not in ['Employee', 'Admin']:
        flash('You do not have permission to edit this player.')
        return redirect(url_for('players.show', id=player.id))
    
    form = PlayerForm()
    if form.validate_on_submit():
        # Handle image upload
        if form.profile_image.data:
            filename = secure_filename(form.profile_image.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            form.profile_image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'players', filename))
            player.profile_image = f'/static/uploads/players/{filename}'
        
        player.name = form.name.data
        player.bio = form.bio.data
        player.country = form.country.data
        player.world_ranking = form.world_ranking.data
        player.pro_since = form.pro_since.data
        player.major_wins = form.major_wins.data
        player.tour_wins = form.tour_wins.data
        
        db.session.commit()
        
        flash('Player updated successfully!')
        return redirect(url_for('players.show', id=player.id))
        
    elif request.method == 'GET':
        form.name.data = player.name
        form.bio.data = player.bio
        form.country.data = player.country
        form.world_ranking.data = player.world_ranking
        form.pro_since.data = player.pro_since
        form.major_wins.data = player.major_wins
        form.tour_wins.data = player.tour_wins
    
    return render_template('players/edit.html', title='Edit Player', form=form, player=player)

@bp.route('/<int:id>/vote', methods=['POST'])
@login_required
def vote(id):
    player = Player.query.filter_by(id=id, approved=True).first_or_404()
    
    # Check if user has already voted
    existing_vote = Vote.query.filter_by(
        user_id=current_user.id,
        player_id=player.id,
        content_type='player'
    ).first()
    
    if existing_vote:
        # Remove vote if it exists
        db.session.delete(existing_vote)
        db.session.commit()
        flash('Your vote has been removed.')
    else:
        # Add new vote
        vote = Vote(
            user_id=current_user.id,
            player_id=player.id,
            content_type='player'
        )
        db.session.add(vote)
        db.session.commit()
        flash('Your vote has been recorded!')
    
    return redirect(url_for('players.show', id=player.id))

@bp.route('/<int:id>/approve', methods=['POST'])
@login_required
def approve(id):
    # Check if user is employee or admin
    if current_user.role.name not in ['Employee', 'Admin']:
        flash('You do not have permission to approve players.')
        return redirect(url_for('main.index'))
    
    player = Player.query.get_or_404(id)
    player.approved = True
    db.session.commit()
    
    flash('Player has been approved!')
    
    # Redirect back to moderator dashboard
    if current_user.role.name == 'Admin':
        return redirect(url_for('main.admin_dashboard'))
    else:
        return redirect(url_for('main.employee_dashboard'))

@bp.route('/<int:id>/verify', methods=['POST'])
@login_required
def verify(id):
    # Check if user is admin
    if current_user.role.name != 'Admin':
        flash('You do not have permission to verify players.')
        return redirect(url_for('main.index'))
    
    player = Player.query.get_or_404(id)
    
    # Get user ID from form
    user_id = request.form.get('user_id', type=int)
    
    if user_id:
        user = User.query.get(user_id)
        if user and user.role.name != 'Player':
            # Update user role to Player
            player_role = db.session.query(Role).filter_by(name='Player').first()
            user.role = player_role
            
        player.user_id = user_id
        player.verified = True
        db.session.commit()
        
        flash(f'Player {player.name} has been verified and linked to user account!')
    else:
        flash('No user selected for verification.')
    
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_players():
    # Check if user is employee or admin
    if current_user.role.name not in ['Employee', 'Admin']:
        flash('You do not have permission to import players.')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file:
            try:
                csv_data = file.read().decode('utf-8')
                csv_file = io.StringIO(csv_data)
                csv_reader = csv.DictReader(csv_file)
                
                players_imported = 0
                for row in csv_reader:
                    player = Player(
                        name=row.get('name', ''),
                        profile_image=row.get('profile_image', ''),
                        bio=row.get('bio', ''),
                        country=row.get('country', ''),
                        world_ranking=int(row.get('world_ranking', 0)),
                        pro_since=int(row.get('pro_since', 0)),
                        major_wins=int(row.get('major_wins', 0)),
                        tour_wins=int(row.get('tour_wins', 0)),
                        submitter=current_user,
                        approved=True
                    )
                    db.session.add(player)
                    players_imported += 1
                
                db.session.commit()
                flash(f'Successfully imported {players_imported} players!')
            except Exception as e:
                flash(f'Error importing CSV file: {str(e)}')
            
            return redirect(url_for('players.index'))
    
    return render_template('players/import.html', title='Import Players')