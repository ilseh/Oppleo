
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
    # %B - month written in English
    valid_from = DateField('Start datum', format='%d %B %Y', validators=[Optional()])
    valid_until = DateField('Eind datum', format='%d %B %Y', validators=[Optional()])

    vehicle_make = StringField('Merk')
    vehicle_model = StringField('Model')
    license_plate = StringField('Kenteken')
    get_odometer = BooleanField('Kilometerregistratie')

    oauth_email = EmailField('e-mail', validators=[Email(), Optional()])
    oauth_password = StringField('password', validators=[Optional()])

    vehicle_name = StringField('Naam')
    vehicle_id = StringField('ID')
    vehicle_vin = StringField('VIN')


    submit = SubmitField('Sign In')
    # recaptcha = RecaptchaField()
