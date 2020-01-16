
from flask_wtf import FlaskForm

from wtforms import StringField, BooleanField, SubmitField, PasswordField
from wtforms.validators import validators, DataRequired, Length, EqualTo

class ChangePasswordForm(FlaskForm):
    # currently only supporting the single admin user
    username = 'admin'
    current_password = StringField('Current password', validators=[
        DataRequired(),
        Length(min=5, max=25),
        ])
    new_password = PasswordField('New password', validators=[
        DataRequired(),
        Length(min=8, max=25),
        EqualTo('confirm', message='Passwords must match') 
        ])
    confirm_password = PasswordField('Confirm password')
    submit = SubmitField('Update Password')
    # recaptcha = RecaptchaField()
