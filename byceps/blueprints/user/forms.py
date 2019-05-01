"""
byceps.blueprints.user.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from uuid import UUID

from wtforms import BooleanField, DateField, HiddenField, PasswordField, \
    StringField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from ...services.user import screen_name_validator
from ...util.l10n import LocalizedForm


class UserCreateForm(LocalizedForm):
    screen_name = StringField('Benutzername', [
        InputRequired(),
        Length(min=screen_name_validator.MIN_LENGTH,
               max=screen_name_validator.MAX_LENGTH),
    ])
    first_names = StringField('Vorname(n)', [InputRequired(), Length(min=2, max=40)])
    last_name = StringField('Nachname', [InputRequired(), Length(min=2, max=40)])
    email_address = StringField('E-Mail-Adresse', [InputRequired(), Length(min=6)])
    password = PasswordField('Passwort', [InputRequired(), Length(min=8)])
    terms_version_id = HiddenField('AGB-Version', [InputRequired()])
    consent_to_terms = BooleanField('AGB', [InputRequired()])
    consent_to_privacy_policy = BooleanField('Datenschutzbestimmungen', [InputRequired()])
    subscribe_to_newsletter = BooleanField('Newsletter')

    def validate_screen_name(form, field):
        if not screen_name_validator.is_screen_name_valid(field.data):
            raise ValidationError(
                'Enthält ungültige Zeichen. Erlaubt sind Buchstaben, '
                ' Ziffern und diese Sonderzeichen: {}' \
                    .format(' '.join(screen_name_validator.SPECIAL_CHARS)))

    def validate_terms_version_id(form, field):
        try:
            UUID(field.data)
        except ValueError:
            raise ValueError('Ungültige AGB-Version.')


class DetailsForm(LocalizedForm):
    first_names = StringField('Vorname(n)', [InputRequired(), Length(min=2)])
    last_name = StringField('Nachname', [InputRequired(), Length(min=2)])
    date_of_birth = DateField('Geburtsdatum',
                              [Optional()],
                              format='%d.%m.%Y')
    country = StringField('Land', [Optional(), Length(max=60)])
    zip_code = StringField('PLZ', [Optional()])
    city = StringField('Stadt', [Optional()])
    street = StringField('Straße', [Optional()])
    phone_number = StringField('Telefonnummer', [Optional(), Length(max=20)])


class RequestConfirmationEmailForm(LocalizedForm):
    screen_name = StringField('Benutzername', [InputRequired()])
