"""
byceps.blueprints.site.user.settings.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g
from wtforms import PasswordField, StringField
from wtforms.fields.html5 import DateField, TelField
from wtforms.validators import InputRequired, Length, Optional

from .....services.authentication.password import service as password_service
from .....services.user import screen_name_validator, service as user_service
from .....util.l10n import LocalizedForm

from ....common.core.forms import ScreenNameValidator


class ChangeScreenNameForm(LocalizedForm):
    screen_name = StringField('Neuer Benutzername', [
        InputRequired(),
        Length(min=screen_name_validator.MIN_LENGTH,
               max=screen_name_validator.MAX_LENGTH),
        ScreenNameValidator(),
    ])
    password = PasswordField('Aktuelles Passwort', [InputRequired()])

    @staticmethod
    def validate_screen_name(form, field):
        if g.current_user.screen_name == field.data:
            raise ValueError('Dies ist bereits der aktuelle Benutzername.')

        if user_service.is_screen_name_already_assigned(field.data):
            raise ValueError('Dieser Benutzername kann nicht verwendet werden.')

    @staticmethod
    def validate_password(form, field):
        user_id = g.current_user.id
        password = field.data

        if not password_service.is_password_valid_for_user(user_id, password):
            raise ValueError('Das Passwort ist nicht korrekt.')


class DetailsForm(LocalizedForm):
    first_names = StringField('Vorname(n)', [InputRequired(), Length(min=2)])
    last_name = StringField('Nachname', [InputRequired(), Length(min=2, max=80)])
    date_of_birth = DateField('Geburtsdatum', [Optional()])
    country = StringField('Land', [Optional(), Length(max=60)])
    zip_code = StringField('PLZ', [Optional()])
    city = StringField('Stadt', [Optional()])
    street = StringField('Straße', [Optional()])
    phone_number = TelField('Telefonnummer', [Optional(), Length(max=20)])
