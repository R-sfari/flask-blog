from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from flask_wtf import FlaskForm


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(2, 64)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(2, 128)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=5000)])
    submit = SubmitField('Send')
