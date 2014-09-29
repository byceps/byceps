# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from itertools import chain
from string import ascii_letters, digits

from wtforms import BooleanField, DateField, FileField, PasswordField, \
    StringField
from wtforms.validators import DataRequired, Optional, ValidationError

from ...util.l10n import LocalizedForm


GERMAN_CHARS = 'äöüß'
SPECIAL_CHARS = '!$&*-./<=>?[]_'
VALID_SCREEN_NAME_CHARS = frozenset(chain(
    ascii_letters, digits, GERMAN_CHARS, SPECIAL_CHARS))


class UserCreateForm(LocalizedForm):
    screen_name = StringField('Benutzername', validators=[DataRequired()])
    email_address = StringField('E-Mail-Adresse', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    consent_to_terms = BooleanField('AGB', validators=[DataRequired()])
    subscribe_to_newsletter = BooleanField('Newsletter')

    def validate_screen_name(form, field):
        if not all(map(VALID_SCREEN_NAME_CHARS.__contains__, field.data)):
            raise ValidationError(
                'Enthält ungültige Zeichen. Erlaubt sind Buchstaben, '
                ' Ziffern und diese Sonderzeichen: {}'.format(SPECIAL_CHARS))


class DetailsForm(LocalizedForm):
    first_names = StringField('Vorname(n)')
    last_name = StringField('Nachname')
    date_of_birth = DateField('Geburtsdatum',
                              format='%d.%m.%Y',
                              validators=[Optional()])
    zip_code = StringField('PLZ', validators=[Optional()])
    city = StringField('Stadt', validators=[Optional()])
    street = StringField('Straße', validators=[Optional()])


class AvatarImageUpdateForm(LocalizedForm):
    image = FileField('Bilddatei')


class RequestConfirmationEmailForm(LocalizedForm):
    screen_name = StringField('Benutzername', validators=[DataRequired()])


class LoginForm(LocalizedForm):
    screen_name = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    permanent = BooleanField()
