# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from itertools import chain
from string import ascii_letters, digits

from flask import g
from wtforms import BooleanField, DateField, FileField, PasswordField, \
    StringField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, \
    ValidationError

from ...util.l10n import LocalizedForm


GERMAN_CHARS = 'äöüß'
SPECIAL_CHARS = '!$&*-./<=>?[]_'
VALID_SCREEN_NAME_CHARS = frozenset(chain(
    ascii_letters, digits, GERMAN_CHARS, SPECIAL_CHARS))


class UserCreateForm(LocalizedForm):
    screen_name = StringField('Benutzername', [DataRequired(), Length(min=4)])
    email_address = StringField('E-Mail-Adresse', [DataRequired(), Length(min=6)])
    password = PasswordField('Passwort', [DataRequired()])
    consent_to_terms = BooleanField('AGB', [DataRequired()])
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
                              [Optional()],
                              format='%d.%m.%Y')
    zip_code = StringField('PLZ', [Optional()])
    city = StringField('Stadt', [Optional()])
    street = StringField('Straße', [Optional()])


class AvatarImageUpdateForm(LocalizedForm):
    image = FileField('Bilddatei')


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


class UpdatePasswordForm(LocalizedForm):
    old_password = PasswordField('Bisheriges Passwort', [DataRequired()])
    new_password = PasswordField(
        'Neues Passwort',
        get_new_password_validators('new_password_confirmation'))
    new_password_confirmation = PasswordField(
        'Neues Passwort (Wiederholung)',
        get_new_password_validators('new_password'))

    def validate_old_password(form, field):
        if not g.current_user.is_password_valid(field.data):
            raise ValidationError(
                'Das eingegebene Passwort stimmt nicht mit dem bisherigen überein.')


class LoginForm(LocalizedForm):
    screen_name = StringField('Benutzername', [DataRequired()])
    password = PasswordField('Passwort', [DataRequired()])
    permanent = BooleanField()
