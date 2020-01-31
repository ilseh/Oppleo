
from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class AuthorizeForm(FlaskForm):
    password = StringField('password', validators=[DataRequired()])
    submit = SubmitField('Sign In')
    # recaptcha = RecaptchaField()
