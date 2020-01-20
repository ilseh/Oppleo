
from flask_wtf import FlaskForm

from wtforms import StringField, BooleanField, SubmitField, DateField, HiddenField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Optional, Email

class RfidChangeForm(FlaskForm):
    rfid = HiddenField('rfid')  # - read-only, no editing
    name = StringField('Naam')
    enabled = BooleanField('Actief')    # Required() validator only accepts True
    # created_at - read-only, no editing
    # last_used_at - read-only, no editing
    valid_from = DateField('Start datum', format='%d %m %Y', validators=[Optional()])
    valid_until = DateField('Eind datum', format='%d %m %Y', validators=[Optional()])

    vehicle_make = StringField('Naam')
    vehicle_model = StringField('Naam')
    license_plate = StringField('Naam')
    get_odometer = BooleanField('Kilometerregistratie')

    oauth_email = EmailField('e-mail', validators=[Email(), Optional()])
    oauth_password = StringField('password', validators=[Optional()])

    submit = SubmitField('Sign In')
    # recaptcha = RecaptchaField()
