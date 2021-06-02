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


class NewPasswordLength(Length):
    def __init__(self) -> None:
        super().__init__(
            min=MINIMUM_PASSWORD_LENGTH, max=MAXIMUM_PASSWORD_LENGTH
        )


class PasswordConfirmationMatches(EqualTo):
    def __init__(self, companion_field_name: str) -> None:
        super().__init__(
            companion_field_name,
            message=lazy_gettext(
                'The new password and its confirmation must match.'
            ),
        )


class RequestResetForm(LocalizedForm):
    screen_name = StringField(lazy_gettext('Username'), [InputRequired()])


class ResetForm(LocalizedForm):
    new_password = PasswordField(
        lazy_gettext('New password'),
        [
            InputRequired(),
            NewPasswordLength(),
        ],
    )
    new_password_confirmation = PasswordField(
        lazy_gettext('New password (confirmation)'),
        [
            InputRequired(),
            PasswordConfirmationMatches('new_password'),
        ],
    )


class UpdateForm(ResetForm):
    old_password = PasswordField(
        lazy_gettext('Current password'), [InputRequired()]
    )

    @staticmethod
    def validate_old_password(form, field):
        user_id = g.user.id
        password = field.data

        if not password_service.is_password_valid_for_user(user_id, password):
            raise ValidationError(
                lazy_gettext('The password does not match the current one.')
            )
