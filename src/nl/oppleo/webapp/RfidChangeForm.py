
from flask_wtf import FlaskForm

from wtforms import StringField, BooleanField, SubmitField, DateField, HiddenField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Optional, Email

import logging

class RfidChangeForm(FlaskForm):

    ENGLISH = 0
    DUTCH = 1

    logger = logging.getLogger('nl.oppleo.webapp.RfidChangeForm')

    rfid = HiddenField('rfid')  # - read-only, no editing
    name = StringField('Naam')
    enabled = BooleanField('Actief')    # Required() validator only accepts True
    # created_at - read-only, no editing
    # last_used_at - read-only, no editing
    # %B - month written in English
    valid_from = DateField(label='Start datum', format='%d %B %Y', validators=[Optional()])
    valid_until = DateField(label='Eind datum', format='%d %B %Y', validators=[Optional()])

    vehicle_make = StringField('Merk')
    vehicle_model = StringField('Model')
    license_plate = StringField('Kenteken')
    get_odometer = BooleanField('Kilometerregistratie')

    oauth_email = EmailField('e-mail', validators=[Email(), Optional()])
    oauth_password = StringField('password', validators=[Optional()])

    vehicle_name = StringField('Naam')
    vehicle_vin = StringField('VIN')

    submit = SubmitField('Sign In')
    # recaptcha = RecaptchaField()

    def translateErrors(self, lang=None):
        if lang == None: 
            lang = RfidChangeForm.ENGLISH
        errors = self.errors
        translatedErrors = {}

        # Iterate through the fields to translate the error texts
        for field_num, field_name in enumerate(self.errors, start=1):
            print("error {}: {}".format(field_num, field_name))
            translated_field_name = getattr(self, field_name).label.text
            translatedErrors[translated_field_name] = []
            # Iterate through the errors per field
            for error_num, error_text in enumerate(self.errors[field_name], start=1):
                print("Error field #{} ({}) error #{}: {}".format(field_num, field_name, error_num, error_text))
                if error_text == 'Not a valid date value':
                    translatedErrors[translated_field_name].append('Geen geldige datum')
                    "Invalid email address."
                elif error_text == 'Invalid email address.':
                    translatedErrors[translated_field_name].append('Ongeldig formaat')
                else:
                    self.logger.warning('No translation for "{}"'.format(error_text))
                    translatedErrors[translated_field_name].append(error_text)

        return translatedErrors