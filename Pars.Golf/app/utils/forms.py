from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange, URL, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
        
        if not User.validate_username(username.data):
            raise ValidationError('Username can only contain letters, numbers, and underscores.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class EditProfileForm(FlaskForm):
    profile_image = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    bio = TextAreaField('About Me', validators=[Length(max=500)])
    submit = SubmitField('Save Changes')

class ClubForm(FlaskForm):
    name = StringField('Club Name', validators=[DataRequired(), Length(max=100)])
    brand = StringField('Brand', validators=[DataRequired(), Length(max=100)])
    club_type = SelectField('Club Type', 
                            choices=[
                                ('driver', 'Driver'),
                                ('wood', 'Fairway Wood'),
                                ('hybrid', 'Hybrid'),
                                ('iron', 'Iron'),
                                ('wedge', 'Wedge'),
                                ('putter', 'Putter'),
                                ('set', 'Complete Set')
                            ],
                            validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Club Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    purchase_link = StringField('Purchase Link', validators=[URL(), Optional()])
    price = FloatField('Price (USD)', validators=[NumberRange(min=0), Optional()])
    release_year = IntegerField('Release Year', validators=[Optional()])
    submit = SubmitField('Submit Club')

class PlayerForm(FlaskForm):
    name = StringField('Player Name', validators=[DataRequired(), Length(max=100)])
    profile_image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    bio = TextAreaField('Biography', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired(), Length(max=100)])
    world_ranking = IntegerField('World Ranking', validators=[Optional()])
    pro_since = IntegerField('Pro Since (Year)', validators=[Optional()])
    major_wins = IntegerField('Major Wins', validators=[NumberRange(min=0), Optional()])
    tour_wins = IntegerField('Tour Wins', validators=[NumberRange(min=0), Optional()])
    submit = SubmitField('Submit Player')

class CourseForm(FlaskForm):
    name = StringField('Course Name', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Course Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    website = StringField('Website', validators=[URL(), Optional()])
    par = IntegerField('Par', validators=[NumberRange(min=54, max=80), Optional()])
    length_yards = IntegerField('Length (Yards)', validators=[NumberRange(min=5000, max=8000), Optional()])
    difficulty_rating = FloatField('Difficulty Rating (1-10)', validators=[NumberRange(min=1, max=10), Optional()])
    year_built = IntegerField('Year Built', validators=[Optional()])
    designer = StringField('Designer', validators=[Length(max=100), Optional()])
    is_public = BooleanField('Public Course')
    has_hosted_major = BooleanField('Has Hosted Major Tournament')
    submit = SubmitField('Submit Course')