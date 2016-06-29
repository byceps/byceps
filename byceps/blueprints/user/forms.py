# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import chain
from string import ascii_letters, digits

from flask import g
from wtforms import BooleanField, DateField, PasswordField, StringField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, \
    ValidationError

from ...util.l10n import LocalizedForm

from ..authentication import service as authentication_service


GERMAN_CHARS = 'äöüß'
SPECIAL_CHARS = '!$&*-./<=>?[]_'
VALID_SCREEN_NAME_CHARS = frozenset(chain(
    ascii_letters, digits, GERMAN_CHARS, SPECIAL_CHARS))


class UserCreateForm(LocalizedForm):
    screen_name = StringField('Benutzername', [DataRequired(), Length(min=4)])
    first_names = StringField('Vorname(n)', [DataRequired(), Length(min=2)])
    last_name = StringField('Nachname', [DataRequired(), Length(min=2)])
    email_address = StringField('E-Mail-Adresse', [DataRequired(), Length(min=6)])
    password = PasswordField('Passwort', [DataRequired(), Length(min=8)])
    consent_to_terms = BooleanField('AGB', [DataRequired()])
    subscribe_to_newsletter = BooleanField('Newsletter')

    def validate_screen_name(form, field):
        if not all(map(VALID_SCREEN_NAME_CHARS.__contains__, field.data)):
            raise ValidationError(
                'Enthält ungültige Zeichen. Erlaubt sind Buchstaben, '
                ' Ziffern und diese Sonderzeichen: {}'.format(SPECIAL_CHARS))


class DetailsForm(LocalizedForm):
    first_names = StringField('Vorname(n)', [DataRequired(), Length(min=2)])
    last_name = StringField('Nachname', [DataRequired(), Length(min=2)])
    date_of_birth = DateField('Geburtsdatum',
                              [Optional()],
                              format='%d.%m.%Y')
    country = StringField('Land', [Optional(), Length(max=60)])
    zip_code = StringField('PLZ', [Optional()])
    city = StringField('Stadt', [Optional()])
    street = StringField('Straße', [Optional()])
    phone_number = StringField('Telefonnummer', [Optional(), Length(max=20)])


class RequestConfirmationEmailForm(LocalizedForm):
    screen_name = StringField('Benutzername', [DataRequired()])


class RequestPasswordResetForm(LocalizedForm):
    screen_name = StringField('Benutzername', [DataRequired()])


def get_new_password_validators(companion_field_name):
    return [
        DataRequired(),
        EqualTo(companion_field_name,
                message='Das neue Passwort muss mit der Wiederholung übereinstimmen.'),
        Length(min=8),
    ]


class ResetPasswordForm(LocalizedForm):
    new_password = PasswordField(
        'Neues Passwort',
        get_new_password_validators('new_password_confirmation'))
    new_password_confirmation = PasswordField(
        'Neues Passwort (Wiederholung)',
        get_new_password_validators('new_password'))


class UpdatePasswordForm(ResetPasswordForm):
    old_password = PasswordField('Bisheriges Passwort', [DataRequired()])

    def validate_old_password(form, field):
        user = g.current_user
        password = field.data

        if not authentication_service.is_password_valid_for_user(user, password):
            raise ValidationError(
                'Das eingegebene Passwort stimmt nicht mit dem bisherigen überein.')
