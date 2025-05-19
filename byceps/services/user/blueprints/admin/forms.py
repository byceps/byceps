"""
byceps.services.user.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import re

from flask_babel import lazy_gettext, pgettext
from wtforms import (
    DateField,
    PasswordField,
    SelectField,
    StringField,
    TelField,
    TextAreaField,
)
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from byceps.services.core.blueprints.common.forms import ScreenNameValidator
from byceps.services.site import site_service
from byceps.services.user import screen_name_validator, user_service
from byceps.util.l10n import LocalizedForm


EMAIL_ADDRESS_PATTERN = re.compile(r'^.+?@.+?\..+?$')

MINIMUM_PASSWORD_LENGTH = 10
MAXIMUM_PASSWORD_LENGTH = 100

ACCOUNT_DELETION_VERIFICATION_TEXT = 'delete account'


def validate_email_address(form, field):
    if EMAIL_ADDRESS_PATTERN.search(field.data) is None:
        raise ValidationError(lazy_gettext('Invalid email address'))

    if user_service.is_email_address_already_assigned(field.data):
        raise ValidationError(
            lazy_gettext('This email address is not available.')
        )


def validate_screen_name_availability(form, field):
    if user_service.is_screen_name_already_assigned(field.data):
        raise ValidationError(lazy_gettext('This username is not available.'))


class CreateAccountForm(LocalizedForm):
    screen_name = StringField(
        lazy_gettext('Username'),
        [
            InputRequired(),
            Length(
                min=screen_name_validator.MIN_LENGTH,
                max=screen_name_validator.MAX_LENGTH,
            ),
            ScreenNameValidator(),
            validate_screen_name_availability,
        ],
    )
    first_name = StringField(
        lazy_gettext('First name'), [InputRequired(), Length(min=2, max=40)]
    )
    last_name = StringField(
        lazy_gettext('Last name'), [InputRequired(), Length(min=2, max=80)]
    )
    email_address = StringField(
        lazy_gettext('Email address'),
        [InputRequired(), Length(min=6, max=120), validate_email_address],
    )
    password = PasswordField(
        lazy_gettext('Password'),
        [
            InputRequired(),
            Length(min=MINIMUM_PASSWORD_LENGTH, max=MAXIMUM_PASSWORD_LENGTH),
        ],
    )
    site_id = SelectField(lazy_gettext('Site ID'), validators=[Optional()])

    def set_site_choices(self):
        sites = site_service.get_all_sites()
        sites = [site for site in sites if site.enabled]
        sites.sort(key=lambda site: site.id)

        choices = [(str(site.id), site.id) for site in sites]
        choices.insert(0, ('', '<' + pgettext('site', 'none') + '>'))
        self.site_id.choices = choices


class SuspendAccountForm(LocalizedForm):
    reason = TextAreaField(
        lazy_gettext('Reason'),
        validators=[InputRequired(), Length(max=1000)],
    )


class DeleteAccountForm(LocalizedForm):
    reason = TextAreaField(
        lazy_gettext('Reason'),
        validators=[InputRequired(), Length(max=1000)],
    )
    verification = StringField(
        lazy_gettext('Confirmation'), validators=[InputRequired()]
    )

    @staticmethod
    def validate_verification(form, field):
        if field.data != ACCOUNT_DELETION_VERIFICATION_TEXT:
            raise ValidationError(lazy_gettext('Invalid confirmation word'))


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
            validate_screen_name_availability,
        ],
    )
    reason = TextAreaField(
        lazy_gettext('Reason'),
        validators=[InputRequired(), Length(max=1000)],
    )


class ChangeEmailAddressForm(LocalizedForm):
    email_address = StringField(
        lazy_gettext('New email address'),
        [InputRequired(), Length(min=6, max=120), validate_email_address],
    )
    reason = TextAreaField(
        lazy_gettext('Reason'),
        validators=[InputRequired(), Length(max=1000)],
    )


class InvalidateEmailAddressForm(LocalizedForm):
    reason = TextAreaField(
        lazy_gettext('Reason'),
        validators=[InputRequired(), Length(max=1000)],
    )


class ChangeDetailsForm(LocalizedForm):
    first_name = StringField(
        lazy_gettext('First name'), [InputRequired(), Length(min=2)]
    )
    last_name = StringField(
        lazy_gettext('Last name'), [InputRequired(), Length(min=2, max=80)]
    )
    date_of_birth = DateField(lazy_gettext('Date of birth'), [Optional()])
    country = StringField(lazy_gettext('Country'), [Optional(), Length(max=60)])
    postal_code = StringField(lazy_gettext('Postal code'), [Optional()])
    city = StringField(lazy_gettext('City'), [Optional()])
    street = StringField(lazy_gettext('Street'), [Optional()])
    phone_number = TelField(
        lazy_gettext('Phone number'), [Optional(), Length(max=20)]
    )


class SetPasswordForm(LocalizedForm):
    password = PasswordField(
        lazy_gettext('Password'),
        [
            InputRequired(),
            Length(min=MINIMUM_PASSWORD_LENGTH, max=MAXIMUM_PASSWORD_LENGTH),
        ],
    )
