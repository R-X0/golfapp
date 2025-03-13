from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.content import Club, Vote
from app.utils.forms import ClubForm
from werkzeug.utils import secure_filename
import os
import csv
import io
from datetime import datetime

bp = Blueprint('clubs', __name__, url_prefix='/clubs')

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'votes')
    filter_brand = request.args.get('brand')
    filter_type = request.args.get('type')
    
    query = Club.query.filter_by(approved=True)
    
    if filter_brand:
        query = query.filter_by(brand=filter_brand)
    
    if filter_type:
        query = query.filter_by(club_type=filter_type)
    
    if sort_by == 'votes':
        clubs = query.join(Vote, Club.id == Vote.club_id)\
            .group_by(Club.id)\
            .order_by(db.func.count(Vote.id).desc())\
            .paginate(page=page, per_page=12)
    elif sort_by == 'newest':
        clubs = query.order_by(Club.created_at.desc()).paginate(page=page, per_page=12)
    elif sort_by == 'name':
        clubs = query.order_by(Club.name).paginate(page=page, per_page=12)
    else:
        clubs = query.join(Vote, Club.id == Vote.club_id)\
            .group_by(Club.id)\
            .order_by(db.func.count(Vote.id).desc())\
            .paginate(page=page, per_page=12)
    
    # Get unique brands and club types for filtering
    brands = db.session.query(Club.brand).distinct().all()
    club_types = db.session.query(Club.club_type).distinct().all()
    
    return render_template('clubs/index.html', 
                           title='Golf Clubs',
                           clubs=clubs,
                           brands=[brand[0] for brand in brands],
                           club_types=[club_type[0] for club_type in club_types],
                           current_sort=sort_by,
                           current_brand=filter_brand,
                           current_type=filter_type)

@bp.route('/<int:id>')
def show(id):
    club = Club.query.filter_by(id=id, approved=True).first_or_404()
    
    # Check if current user has voted for this club
    user_voted = False
    if current_user.is_authenticated:
        vote = Vote.query.filter_by(
            user_id=current_user.id,
            club_id=club.id,
            content_type='club'
        ).first()
        user_voted = vote is not None
    
    # Get similar clubs
    similar_clubs = Club.query.filter_by(
        club_type=club.club_type, 
        approved=True
    ).filter(Club.id != club.id).limit(4).all()
    
    return render_template('clubs/show.html', 
                           title=f'{club.brand} {club.name}',
                           club=club,
                           user_voted=user_voted,
                           similar_clubs=similar_clubs)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = ClubForm()
    if form.validate_on_submit():
        # Handle image upload
        image_url = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            form.image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'clubs', filename))
            image_url = f'/static/uploads/clubs/{filename}'
        
        # Create club
        club = Club(
            name=form.name.data,
            brand=form.brand.data,
            club_type=form.club_type.data,
            description=form.description.data,
            image_url=image_url,
            purchase_link=form.purchase_link.data,
            price=form.price.data,
            release_year=form.release_year.data,
            submitter=current_user,
            # Set approved to True if user is Employee or Admin
            approved=current_user.role.name in ['Employee', 'Admin']
        )
        
        db.session.add(club)
        db.session.commit()
        
        flash('Your club has been submitted for approval!' if not club.approved else 'Club added successfully!')
        return redirect(url_for('clubs.show', id=club.id))
    
    return render_template('clubs/new.html', title='Add Club', form=form)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    club = Club.query.get_or_404(id)
    
    # Check if user is submitter, employee or admin
    if club.submitter != current_user and current_user.role.name not in ['Employee', 'Admin']:
        flash('You do not have permission to edit this club.')
        return redirect(url_for('clubs.show', id=club.id))
    
    form = ClubForm()
    if form.validate_on_submit():
        # Handle image upload
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            form.image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'clubs', filename))
            club.image_url = f'/static/uploads/clubs/{filename}'
        
        club.name = form.name.data
        club.brand = form.brand.data
        club.club_type = form.club_type.data
        club.description = form.description.data
        club.purchase_link = form.purchase_link.data
        club.price = form.price.data
        club.release_year = form.release_year.data
        
        db.session.commit()
        
        flash('Club updated successfully!')
        return redirect(url_for('clubs.show', id=club.id))
        
    elif request.method == 'GET':
        form.name.data = club.name
        form.brand.data = club.brand
        form.club_type.data = club.club_type
        form.description.data = club.description
        form.purchase_link.data = club.purchase_link
        form.price.data = club.price
        form.release_year.data = club.release_year
    
    return render_template('clubs/edit.html', title='Edit Club', form=form, club=club)

@bp.route('/<int:id>/vote', methods=['POST'])
@login_required
def vote(id):
    club = Club.query.filter_by(id=id, approved=True).first_or_404()
    
    # Check if user has already voted
    existing_vote = Vote.query.filter_by(
        user_id=current_user.id,
        club_id=club.id,
        content_type='club'
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
            club_id=club.id,
            content_type='club'
        )
        db.session.add(vote)
        db.session.commit()
        flash('Your vote has been recorded!')
    
    return redirect(url_for('clubs.show', id=club.id))

@bp.route('/<int:id>/approve', methods=['POST'])
@login_required
def approve(id):
    # Check if user is employee or admin
    if current_user.role.name not in ['Employee', 'Admin']:
        flash('You do not have permission to approve clubs.')
        return redirect(url_for('main.index'))
    
    club = Club.query.get_or_404(id)
    club.approved = True
    db.session.commit()
    
    flash('Club has been approved!')
    
    # Redirect back to moderator dashboard
    if current_user.role.name == 'Admin':
        return redirect(url_for('main.admin_dashboard'))
    else:
        return redirect(url_for('main.employee_dashboard'))

@bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_clubs():
    # Check if user is employee or admin
    if current_user.role.name not in ['Employee', 'Admin']:
        flash('You do not have permission to import clubs.')
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
                
                clubs_imported = 0
                for row in csv_reader:
                    club = Club(
                        name=row.get('name', ''),
                        brand=row.get('brand', ''),
                        club_type=row.get('club_type', ''),
                        description=row.get('description', ''),
                        image_url=row.get('image_url', ''),
                        purchase_link=row.get('purchase_link', ''),
                        price=float(row.get('price', 0)),
                        release_year=int(row.get('release_year', 0)),
                        submitter=current_user,
                        approved=True
                    )
                    db.session.add(club)
                    clubs_imported += 1
                
                db.session.commit()
                flash(f'Successfully imported {clubs_imported} clubs!')
            except Exception as e:
                flash(f'Error importing CSV file: {str(e)}')
            
            return redirect(url_for('clubs.index'))
    
    return render_template('clubs/import.html', title='Import Clubs')