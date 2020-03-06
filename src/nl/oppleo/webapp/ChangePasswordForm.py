
from flask_wtf import FlaskForm

from wtforms import StringField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo

class ChangePasswordForm(FlaskForm):
    current_password = StringField('Current password', validators=[
        DataRequired(),
        Length(min=5, max=25)
        ])
    show_current_password = BooleanField()
    new_password = PasswordField('New password', validators=[
        DataRequired(),
        Length(min=8, max=25)
        ])
    show_new_password = BooleanField()
    confirm_password = PasswordField('Confirm password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    show_confirm_password = BooleanField()
    submit = SubmitField('Update Password')

    # recaptcha = RecaptchaField()
