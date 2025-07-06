from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Login')

class OrderForm(FlaskForm):
    amount = IntegerField('Anzahl Karten', validators=[DataRequired(), NumberRange(min=0)])
    comment = TextAreaField('Bemerkung', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Bestellung absenden')

class UserForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Benutzer anlegen')

class GameForm(FlaskForm):
    opponent = StringField('Gegner', validators=[DataRequired()])
    date = StringField('Datum (YYYY-MM-DD)', validators=[DataRequired()])
    deadline = StringField('Bestellfrist (YYYY-MM-DD)', validators=[Optional()])
    submit = SubmitField('Spiel speichern')
