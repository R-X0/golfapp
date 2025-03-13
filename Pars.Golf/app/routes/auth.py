from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User, Role
from app.utils.forms import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm
from app.utils.email import send_password_reset_email
from app.utils.oauth import OAuthSignIn

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # Basic security check to make sure next_page is a relative URL
        if not next_page or next_page.startswith('http'):
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        if not User.validate_username(form.username.data):
            flash('Username can only contain letters, numbers, and underscores')
            return redirect(url_for('auth.register'))
        
        user_role = Role.query.filter_by(name='User').first()
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=user_role
        )
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@bp.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    
    oauth = OAuthSignIn.get_provider(provider)
    oauth_id, email, username = oauth.callback()
    
    if oauth_id is None:
        flash('Authentication failed.')
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(email=email).first()
    if user is None:
        # Ensure username is unique
        base_username = username.lower().replace(' ', '_')
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first() is not None:
            username = f"{base_username}{counter}"
            counter += 1
        
        user_role = Role.query.filter_by(name='User').first()
        user = User(
            username=username,
            email=email,
            role=user_role,
            oauth_provider=provider,
            oauth_id=oauth_id
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user, True)
    return redirect(url_for('main.index'))

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)