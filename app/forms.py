#Bis und mit Zeile 70 mehrheitlich aus Emanuel Grimbergs Blog übernommen
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, FloatField, IntegerField, TimeField, HiddenField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length, NumberRange
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Merke mein Login!')
    submit = SubmitField('Anmelden')


class RegistrationForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Benutzername bereits vergeben.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Bitte definiere ein Passwort.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Passwort vergessen')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), EqualTo('Passwort')])
    submit = SubmitField('Neues Passwort erstellen')


class EditProfileForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    about_me = TextAreaField('Ueber mich', validators=[Length(min=0, max=140)])
    submit = SubmitField('Absenden')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Benutzername bereits vergeben.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Absenden')

class PostForm(FlaskForm):
    post = TextAreaField('Sag etwas', validators=[DataRequired()])
    submit = SubmitField('Absenden')
#Bis und mit Zeile 91 eigener Code
class TerrariumForm(FlaskForm):
    terrarium_id = HiddenField()
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=64)])
    size = FloatField('Size', validators=[DataRequired(), NumberRange(min=0.0, max=100.0)])
    optimal_humidity = IntegerField('Optimal Humidity', validators=[DataRequired(), NumberRange(min=0, max=100)])
    optimal_temperature = IntegerField('Optimal Temperature', validators=[DataRequired(), NumberRange(min=0, max=100)])
    actual_humidity = IntegerField('Actual Humidity', validators=[DataRequired(), NumberRange(min=0, max=100)])
    actual_temperature = IntegerField('Actual Temperature', validators=[DataRequired(), NumberRange(min=0, max=100)])
    country = StringField('Country', validators=[DataRequired(), Length(min=1, max=64)])
    sunrise_time = TimeField('Sunrise Time', validators=[DataRequired()])
    sunset_time = TimeField('Sunset Time', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')




