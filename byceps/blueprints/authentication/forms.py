# -*- coding: utf-8 -*-

"""
byceps.blueprints.authentication.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

from ...util.l10n import LocalizedForm

from . import service


MINIMUM_PASSWORD_LENGTH = 10


class LoginForm(LocalizedForm):
    screen_name = StringField('Benutzername', [DataRequired()])
    password = PasswordField('Passwort', [DataRequired()])
    permanent = BooleanField()


class RequestPasswordResetForm(LocalizedForm):
    screen_name = StringField('Benutzername', [DataRequired()])


def _get_new_password_validators(companion_field_name):
    return [
        DataRequired(),
        EqualTo(companion_field_name,
                message='Das neue Passwort muss mit der Wiederholung übereinstimmen.'),
        Length(min=MINIMUM_PASSWORD_LENGTH),
    ]


class ResetPasswordForm(LocalizedForm):
    new_password = PasswordField(
        'Neues Passwort',
        _get_new_password_validators('new_password_confirmation'))
    new_password_confirmation = PasswordField(
        'Neues Passwort (Wiederholung)',
        _get_new_password_validators('new_password'))


class UpdatePasswordForm(ResetPasswordForm):
    old_password = PasswordField('Bisheriges Passwort', [DataRequired()])

    def validate_old_password(form, field):
        user = g.current_user
        password = field.data

        if not service.is_password_valid_for_user(user, password):
            raise ValidationError(
                'Das eingegebene Passwort stimmt nicht mit dem bisherigen überein.')
