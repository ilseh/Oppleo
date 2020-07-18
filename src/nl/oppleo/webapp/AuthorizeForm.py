
from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired

class AuthorizeForm(FlaskForm):
    password = StringField('password', validators=[DataRequired()])
    submit = SubmitField('Sign In')
    extra_field = StringField('extra_field')
    next_page = HiddenField('next_page')

