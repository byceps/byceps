"""
byceps.blueprints.common.authentication.password.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g
from flask_babel import lazy_gettext
from wtforms import PasswordField, StringField
from wtforms.validators import InputRequired, EqualTo, Length, ValidationError

from .....services.authentication.password import service as password_service
from .....util.l10n import LocalizedForm


MINIMUM_PASSWORD_LENGTH = 8
MAXIMUM_PASSWORD_LENGTH = 100


class RequestResetForm(LocalizedForm):
    screen_name = StringField(lazy_gettext('Benutzername'), [InputRequired()])


def _get_new_password_validators(companion_field_name):
    return [
        InputRequired(),
        EqualTo(
            companion_field_name,
            message=lazy_gettext(
                'Das neue Passwort muss mit der Wiederholung übereinstimmen.'
            ),
        ),
        Length(min=MINIMUM_PASSWORD_LENGTH, max=MAXIMUM_PASSWORD_LENGTH),
    ]


class ResetForm(LocalizedForm):
    new_password = PasswordField(
        lazy_gettext('Neues Passwort'),
        _get_new_password_validators('new_password_confirmation'),
    )
    new_password_confirmation = PasswordField(
        lazy_gettext('Neues Passwort (Wiederholung)'),
        _get_new_password_validators('new_password'),
    )


class UpdateForm(ResetForm):
    old_password = PasswordField(
        lazy_gettext('Bisheriges Passwort'), [InputRequired()]
    )

    @staticmethod
    def validate_old_password(form, field):
        user_id = g.user.id
        password = field.data

        if not password_service.is_password_valid_for_user(user_id, password):
            raise ValidationError(
                lazy_gettext(
                    'Das eingegebene Passwort stimmt nicht mit dem bisherigen überein.'
                )
            )
