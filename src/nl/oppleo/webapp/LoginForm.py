
from flask_wtf import FlaskForm

from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me')
    submit = SubmitField('Sign In')
    # recaptcha = RecaptchaField()
