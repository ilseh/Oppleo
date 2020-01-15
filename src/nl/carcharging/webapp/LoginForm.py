
from flask_wtf import FlaskForm

from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=5, max=12, message=None)])
    password = StringField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me')
    submit = SubmitField('Sign In')
    # recaptcha = RecaptchaField()
