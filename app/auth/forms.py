from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, TextAreaField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, EqualTo, regexp, Email, DataRequired
from wtforms import ValidationError
from ..models import User, Role


class LoginForm (FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign in')


class RegistrationForm (FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(2, 64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(2, 64)])
    phone = StringField('Phone', validators=[DataRequired(), Length(2, 64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), regexp('^[A-Za-z][A-Za-z0-9_.]*$', message="Usernames must have only letters, numbers, dots or underscores.")])
    password = PasswordField('Password', render_kw={'description': 'At least 8 characters and 1 digit'}, validators=[DataRequired()])
    second_password = PasswordField('Confirm password', validators=[EqualTo('password', message="Passwords must match.")])
    news_letter = BooleanField('Subscribe to our newsletter.')
    submit = SubmitField('Sign up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already registered.')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Forgot password')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(4, 32)])
    second_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Reset password')


class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(2, 64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(2, 64)])
    phone = StringField('Phone', validators=[DataRequired(), Length(2, 64)])
    about_me = TextAreaField('About me', validators=[DataRequired(), Length(max=2000)])
    birthday = DateField('birthday', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    submit = SubmitField('Update profile')


class EditUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(2, 64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(2, 64)])
    phone = StringField('Phone', validators=[Length(2, 64)])
    email = StringField('Email', validators=[Email(), Length(2, 64)])
    username = StringField('Username', validators=[DataRequired(), Length(2, 64)])
    about_me = TextAreaField('About me', validators=[Length(max=2000)])
    birthday = DateField('birthday')
    address = TextAreaField('Address')
    password = PasswordField('Password', validators=[Length(4, 32)])
    second_password = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match.')])
    role = QuerySelectField(query_factory=lambda: Role.query, get_label='name', blank_text='Select a role...', allow_blank=True)
    submit = SubmitField('Update user')
