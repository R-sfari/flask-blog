from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from flask_wtf.file import FileField, FileRequired
from flask_wtf import FlaskForm


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField(None, render_kw={'id': 'js-markdown-field'}, validators=[DataRequired(), Length(max=4000)])
    file = FileField('Post Image', validators=[FileRequired()])
    submit = SubmitField('Post')


class CommentForm(FlaskForm):
    body = TextAreaField('Write your comment here ...', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Post')