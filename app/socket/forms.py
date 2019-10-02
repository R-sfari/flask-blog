from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SubmitField, StringField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from ..models import User


class RoomForm(FlaskForm):
    name = StringField('Room name', validators=[DataRequired()])
    users = QuerySelectMultipleField(query_factory=lambda: User.query, get_label=lambda user: user.full_name(), blank_text='Select users...', allow_blank=False)
    submit = SubmitField('Create room')
