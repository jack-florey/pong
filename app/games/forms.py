from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
    FieldList,
    FormField
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
)

from app import db
from app.models import Role, User, Player


class PlayerForm(FlaskForm):
        name = StringField('Name')

class SetupGameForm(FlaskForm):
    name = StringField(
        'Name', validators=[InputRequired(),
                             Length(1, 64)])


    players = FieldList(FormField(PlayerForm), min_entries=10)

    submit = SubmitField('Start Game')

    def validate_name(self, field):
        if Player.query.filter_by(name=field.data).first():
            raise ValidationError('Name already registered, please pick another!')


