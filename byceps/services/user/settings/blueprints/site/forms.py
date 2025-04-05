"""
byceps.services.user.settings.blueprints.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import re

from flask import g
from flask_babel import lazy_gettext
from secret_type import secret
from wtforms import DateField, PasswordField, StringField, TelField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from byceps.services.authn.password import authn_password_service
from byceps.services.core.blueprints.common.forms import ScreenNameValidator
from byceps.services.user import screen_name_validator, user_service
from byceps.util.l10n import LocalizedForm


EMAIL_ADDRESS_PATTERN = re.compile(r'^.+?@.+?\..+?$')


def validate_email_address(form, field):
    if EMAIL_ADDRESS_PATTERN.search(field.data) is None:
        raise ValidationError(lazy_gettext('Invalid email address'))

    if user_service.is_email_address_already_assigned(field.data):
        raise ValidationError(
            lazy_gettext('This email address is not available.')
        )


class ChangeEmailAddressForm(LocalizedForm):
    new_email_address = StringField(
        lazy_gettext('New email address'),
        [InputRequired(), Length(min=6, max=120), validate_email_address],
    )
    password = PasswordField(
        lazy_gettext('Current password'), [InputRequired()]
    )

    @staticmethod
    def validate_password(form, field):
        password = secret(field.data)

        if not authn_password_service.is_password_valid_for_user(
            g.user.id, password
        ):
            raise ValidationError(
                lazy_gettext('The password does not match the current one.')
            )


class ChangeScreenNameForm(LocalizedForm):
    screen_name = StringField(
        lazy_gettext('New username'),
        [
            InputRequired(),
            Length(
                min=screen_name_validator.MIN_LENGTH,
                max=screen_name_validator.MAX_LENGTH,
            ),
            ScreenNameValidator(),
        ],
    )
    password = PasswordField(
        lazy_gettext('Current password'), [InputRequired()]
    )

    @staticmethod
    def validate_screen_name(form, field):
        if g.user.screen_name == field.data:
            raise ValidationError(
                lazy_gettext('This already is the current username.')
            )

        if user_service.is_screen_name_already_assigned(field.data):
            raise ValidationError(
                lazy_gettext('This username is not available.')
            )

    @staticmethod
    def validate_password(form, field):
        user_id = g.user.id
        password = secret(field.data)

        if not authn_password_service.is_password_valid_for_user(
            user_id, password
        ):
            raise ValidationError(lazy_gettext('Wrong password.'))


class DetailsForm(LocalizedForm):
    first_name = StringField(
        lazy_gettext('First name'), [InputRequired(), Length(min=2)]
    )
    last_name = StringField(
        lazy_gettext('Last name'), [InputRequired(), Length(min=2, max=80)]
    )
    date_of_birth = DateField(lazy_gettext('Date of birth'), [Optional()])
    country = StringField(lazy_gettext('Country'), [Optional(), Length(max=60)])
    zip_code = StringField(lazy_gettext('Zip code'), [Optional()])
    city = StringField(lazy_gettext('City'), [Optional()])
    street = StringField(lazy_gettext('Street'), [Optional()])
    phone_number = TelField(
        lazy_gettext('Phone number'), [Optional(), Length(max=20)]
    )
