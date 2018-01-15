"""
byceps.blueprints.user.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import chain
from string import ascii_letters, digits
from uuid import UUID

from wtforms import BooleanField, DateField, HiddenField, PasswordField, \
    StringField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from ...util.l10n import LocalizedForm


GERMAN_CHARS = 'äöüß'
SPECIAL_CHARS = '!$&*-./<=>?[]_'
VALID_SCREEN_NAME_CHARS = frozenset(chain(
    ascii_letters, digits, GERMAN_CHARS, SPECIAL_CHARS))


class UserCreateForm(LocalizedForm):
    screen_name = StringField('Benutzername', [InputRequired(), Length(min=4, max=40)])
    first_names = StringField('Vorname(n)', [InputRequired(), Length(min=2, max=40)])
    last_name = StringField('Nachname', [InputRequired(), Length(min=2, max=40)])
    email_address = StringField('E-Mail-Adresse', [InputRequired(), Length(min=6)])
    password = PasswordField('Passwort', [InputRequired(), Length(min=8)])
    terms_version_id = HiddenField('AGB-Version', [InputRequired()])
    consent_to_terms = BooleanField('AGB', [InputRequired()])
    subscribe_to_newsletter = BooleanField('Newsletter')

    def validate_screen_name(form, field):
        if not all(map(VALID_SCREEN_NAME_CHARS.__contains__, field.data)):
            raise ValidationError(
                'Enthält ungültige Zeichen. Erlaubt sind Buchstaben, '
                ' Ziffern und diese Sonderzeichen: {}'.format(SPECIAL_CHARS))

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
