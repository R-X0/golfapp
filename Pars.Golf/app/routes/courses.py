from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.content import Course, Vote
from app.utils.forms import CourseForm
from werkzeug.utils import secure_filename
import os
import csv
import io
from datetime import datetime
import requests

bp = Blueprint('courses', __name__, url_prefix='/courses')

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'votes')
    filter_public = request.args.get('public')
    filter_has_hosted_major = request.args.get('has_hosted_major')
    
    query = Course.query.filter_by(approved=True)
    
    if filter_public:
        is_public = filter_public == 'true'
        query = query.filter_by(is_public=is_public)
    
    if filter_has_hosted_major:
        has_hosted = filter_has_hosted_major == 'true'
        query = query.filter_by(has_hosted_major=has_hosted)
    
    if sort_by == 'votes':
        courses = query.join(Vote, Course.id == Vote.course_id)\
            .group_by(Course.id)\
            .order_by(db.func.count(Vote.id).desc())\
            .paginate(page=page, per_page=12)
    elif sort_by == 'difficulty':
        courses = query.order_by(Course.difficulty_rating.desc()).paginate(page=page, per_page=12)
    elif sort_by == 'name':
        courses = query.order_by(Course.name).paginate(page=page, per_page=12)
    else:
        courses = query.join(Vote, Course.id == Vote.course_id)\
            .group_by(Course.id)\
            .order_by(db.func.count(Vote.id).desc())\
            .paginate(page=page, per_page=12)
    
    return render_template('courses/index.html', 
                           title='Golf Courses',
                           courses=courses,
                           current_sort=sort_by,
                           filter_public=filter_public,
                           filter_has_hosted_major=filter_has_hosted_major)

@bp.route('/<int:id>')
def show(id):
    course = Course.query.filter_by(id=id, approved=True).first_or_404()
    
    # Check if current user has voted for this course
    user_voted = False
    if current_user.is_authenticated:
        vote = Vote.query.filter_by(
            user_id=current_user.id,
            course_id=course.id,
            content_type='course'
        ).first()
        user_voted = vote is not None
    
    # Find similar courses (by location)
    similar_courses = Course.query.filter(
        Course.location.like(f"%{course.location.split(',')[0]}%"), 
        Course.id != course.id,
        Course.approved == True
    ).limit(3).all()
    
    return render_template('courses/show.html', 
                           title=course.name,
                           course=course,
                           user_voted=user_voted,
                           similar_courses=similar_courses)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = CourseForm()
    if form.validate_on_submit():
        # Handle image upload
        image_url = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            form.image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'courses', filename))
            image_url = f'/static/uploads/courses/{filename}'
        
        # Create course
        course = Course(
            name=form.name.data,
            location=form.location.data,
            description=form.description.data,
            image_url=image_url,
            website=form.website.data,
            par=form.par.data,
            length_yards=form.length_yards.data,
            difficulty_rating=form.difficulty_rating.data,
            year_built=form.year_built.data,
            designer=form.designer.data,
            is_public=form.is_public.data,
            has_hosted_major=form.has_hosted_major.data,
            submitter=current_user,
            # Set approved to True if user is Employee or Admin
            approved=current_user.role.name in ['Employee', 'Admin']
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash('Your course has been submitted for approval!' if not course.approved else 'Course added successfully!')
        return redirect(url_for('courses.show', id=course.id))
    
    return render_template('courses/new.html', title='Add Course', form=form)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    course = Course.query.get_or_404(id)
    
    # Check if user is submitter, employee or admin
    if course.submitter != current_user and current_user.role.name not in ['Employee', 'Admin']:
        flash('You do not have permission to edit this course.')
        return redirect(url_for('courses.show', id=course.id))
    
    form = CourseForm()
    if form.validate_on_submit():
        # Handle image upload
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            form.image.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'courses', filename))
            course.image_url = f'/static/uploads/courses/{filename}'
        
        course.name = form.name.data
        course.location = form.location.data
        course.description = form.description.data
        course.website = form.website.data
        course.par = form.par.data
        course.length_yards = form.length_yards.data
        course.difficulty_rating = form.difficulty_rating.data
        course.year_built = form.year_built.data
        course.designer = form.designer.data
        course.is_public = form.is_public.data
        course.has_hosted_major = form.has_hosted_major.data
        
        db.session.commit()
        
        flash('Course updated successfully!')
        return redirect(url_for('courses.show', id=course.id))
        
    elif request.method == 'GET':
        form.name.data = course.name
        form.location.data = course.location
        form.description.data = course.description
        form.website.data = course.website
        form.par.data = course.par
        form.length_yards.data = course.length_yards
        form.difficulty_rating.data = course.difficulty_rating
        form.year_built.data = course.year_built
        form.designer.data = course.designer
        form.is_public.data = course.is_public
        form.has_hosted_major.data = course.has_hosted_major
    
    return render_template('courses/edit.html', title='Edit Course', form=form, course=course)

@bp.route('/<int:id>/vote', methods=['POST'])
@login_required
def vote(id):
    course = Course.query.filter_by(id=id, approved=True).first_or_404()
    
    # Check if user has already voted
    existing_vote = Vote.query.filter_by(
        user_id=current_user.id,
        course_id=course.id,
        content_type='course'
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
            course_id=course.id,
            content_type='course'
        )
        db.session.add(vote)
        db.session.commit()
        flash('Your vote has been recorded!')
    
    return redirect(url_for('courses.show', id=course.id))

@bp.route('/<int:id>/approve', methods=['POST'])
@login_required
def approve(id):
    # Check if user is employee or admin
    if current_user.role.name not in ['Employee', 'Admin']:
        flash('You do not have permission to approve courses.')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(id)
    course.approved = True
    db.session.commit()
    
    flash('Course has been approved!')
    
    # Redirect back to moderator dashboard
    if current_user.role.name == 'Admin':
        return redirect(url_for('main.admin_dashboard'))
    else:
        return redirect(url_for('main.employee_dashboard'))

@bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_courses():
    # Check if user is employee or admin
    if current_user.role.name not in ['Employee', 'Admin']:
        flash('You do not have permission to import courses.')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        if 'csv_file' not in request.files and not request.form.get('use_api'):
            flash('No file part and API option not selected')
            return redirect(request.url)
        
        # Import from CSV
        if 'csv_file' in request.files and request.files['csv_file'].filename != '':
            file = request.files['csv_file']
            try:
                csv_data = file.read().decode('utf-8')
                csv_file = io.StringIO(csv_data)
                csv_reader = csv.DictReader(csv_file)
                
                courses_imported = 0
                for row in csv_reader:
                    course = Course(
                        name=row.get('name', ''),
                        location=row.get('location', ''),
                        description=row.get('description', ''),
                        image_url=row.get('image_url', ''),
                        website=row.get('website', ''),
                        par=int(row.get('par', 72)),
                        length_yards=int(row.get('length_yards', 0)),
                        difficulty_rating=float(row.get('difficulty_rating', 0)),
                        year_built=int(row.get('year_built', 0)),
                        designer=row.get('designer', ''),
                        is_public=row.get('is_public', '').lower() == 'true',
                        has_hosted_major=row.get('has_hosted_major', '').lower() == 'true',
                        submitter=current_user,
                        approved=True
                    )
                    db.session.add(course)
                    courses_imported += 1
                
                db.session.commit()
                flash(f'Successfully imported {courses_imported} courses from CSV!')
            except Exception as e:
                flash(f'Error importing CSV file: {str(e)}')
        
        # Import from API
        elif request.form.get('use_api'):
            try:
                # This is a placeholder for the actual API call
                # In a real implementation, we would use the correct API endpoint and authentication
                api_url = "https://golfapi.io/api/v1/courses"
                # Add API key from config
                api_key = current_app.config.get('GOLF_API_KEY', '')
                
                # For demonstration purposes, we'll mock the API response
                # In a real implementation, this would be:
                # response = requests.get(api_url, headers={'Authorization': f'Bearer {api_key}'})
                # courses_data = response.json()
                
                # Mock data for demonstration
                courses_data = [
                    {
                        "name": "Augusta National Golf Club",
                        "location": "Augusta, Georgia, USA",
                        "description": "Home of the Masters Tournament",
                        "website": "https://www.masters.com",
                        "par": 72,
                        "length_yards": 7475,
                        "difficulty_rating": 9.8,
                        "year_built": 1933,
                        "designer": "Alister MacKenzie, Bobby Jones",
                        "is_public": False,
                        "has_hosted_major": True,
                        "image_url": "/static/img/courses/augusta.jpg"
                    },
                    {
                        "name": "St Andrews Links (Old Course)",
                        "location": "St Andrews, Scotland, UK",
                        "description": "The home of golf",
                        "website": "https://www.standrews.com",
                        "par": 72,
                        "length_yards": 6721,
                        "difficulty_rating": 9.2,
                        "year_built": 1552,
                        "designer": "Mother Nature",
                        "is_public": True,
                        "has_hosted_major": True,
                        "image_url": "/static/img/courses/st_andrews.jpg"
                    }
                ]
                
                courses_imported = 0
                for course_data in courses_data:
                    course = Course(
                        name=course_data.get('name', ''),
                        location=course_data.get('location', ''),
                        description=course_data.get('description', ''),
                        image_url=course_data.get('image_url', ''),
                        website=course_data.get('website', ''),
                        par=course_data.get('par', 72),
                        length_yards=course_data.get('length_yards', 0),
                        difficulty_rating=course_data.get('difficulty_rating', 0),
                        year_built=course_data.get('year_built', 0),
                        designer=course_data.get('designer', ''),
                        is_public=course_data.get('is_public', True),
                        has_hosted_major=course_data.get('has_hosted_major', False),
                        submitter=current_user,
                        approved=True
                    )
                    db.session.add(course)
                    courses_imported += 1
                
                db.session.commit()
                flash(f'Successfully imported {courses_imported} courses from API!')
            except Exception as e:
                flash(f'Error importing from API: {str(e)}')
            
        return redirect(url_for('courses.index'))
    
    return render_template('courses/import.html', title='Import Courses')