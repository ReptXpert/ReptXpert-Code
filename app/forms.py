#Bis und mit Zeile 70 mehrheitlich aus Emanuel Grimbergs Blog übernommen
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, FloatField, IntegerField, TimeField, HiddenField, DateField
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
    size = FloatField('Grösse', validators=[DataRequired(), NumberRange(min=0.0, max=100.0)])
    optimal_humidity = IntegerField('Optimale Luftfeuchtigkeit', validators=[DataRequired(), NumberRange(min=0, max=100)])
    optimal_temperature = IntegerField('Optimale Temperatur', validators=[DataRequired(), NumberRange(min=0, max=100)])
    actual_humidity = IntegerField('Aktuelle Luftfeuchtigkeit', validators=[DataRequired(), NumberRange(min=0, max=100)])
    actual_temperature = IntegerField('Aktuelle Temperatur', validators=[DataRequired(), NumberRange(min=0, max=100)])
    country = StringField('Land', validators=[DataRequired(), Length(min=1, max=64)])
    sunrise_time = TimeField('Sonnenaufgang', validators=[DataRequired()])
    sunset_time = TimeField('Sonnenuntergang', validators=[DataRequired()])
    notes = TextAreaField('Notizen', validators=[Length(min=0, max=140)])
    submit = SubmitField('Absenden')
    

class EventForm(FlaskForm):
    title = StringField('Titel', validators=[DataRequired()])
    start_date = DateField('Start Datum', validators=[DataRequired()], format='%d-%m-%y')
    start_time = TimeField('Start Zeit', validators=[DataRequired()], format='%H:%M')
    end_date = DateField('End Datum', validators=[DataRequired()], format='%d-%m-%y')
    end_time = TimeField('End Zeit', validators=[DataRequired()], format='%H:%M')
    location = StringField('Ort')
    submit = SubmitField('Absenden')
    
    



