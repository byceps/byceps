"""
byceps.blueprints.admin.user.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext, pgettext
from wtforms import PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from ....services.site import service as site_service
from ....services.user import screen_name_validator
from ....util.l10n import LocalizedForm

from ...common.core.forms import ScreenNameValidator


MINIMUM_PASSWORD_LENGTH = 10
MAXIMUM_PASSWORD_LENGTH = 100


class ChangeEmailAddressForm(LocalizedForm):
    email_address = StringField(
        lazy_gettext('New email address'),
        [InputRequired(), Length(min=6, max=120)],
    )
    reason = TextAreaField(
        lazy_gettext('Reason'),
        validators=[InputRequired(), Length(max=1000)],
    )


class ChangeScreenNameForm(LocalizedForm):
    screen_name = StringField(
        lazy_gettext('Neuer username'),
        [
            InputRequired(),
            Length(
                min=screen_name_validator.MIN_LENGTH,
                max=screen_name_validator.MAX_LENGTH,
            ),
            ScreenNameValidator(),
        ],
    )
    reason = TextAreaField(
        lazy_gettext('Reason'),
        validators=[InputRequired(), Length(max=1000)],
    )


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
        ],
    )
    first_names = StringField(
        lazy_gettext('First name(s)'), [InputRequired(), Length(min=2, max=40)]
    )
    last_name = StringField(
        lazy_gettext('Last name(s)'), [InputRequired(), Length(min=2, max=80)]
    )
    email_address = StringField(
        lazy_gettext('Email address'),
        [InputRequired(), Length(min=6, max=120)],
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
        choices.insert(0, ('', pgettext('site', '<none>')))
        self.site_id.choices = choices


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
        if field.data != 'löschen':
            raise ValidationError(lazy_gettext('Invalid confirmation word'))


class SetPasswordForm(LocalizedForm):
    password = PasswordField(
        lazy_gettext('Password'),
        [
            InputRequired(),
            Length(min=MINIMUM_PASSWORD_LENGTH, max=MAXIMUM_PASSWORD_LENGTH),
        ],
    )


class SuspendAccountForm(LocalizedForm):
    reason = TextAreaField(
        lazy_gettext('Reason'),
        validators=[InputRequired(), Length(max=1000)],
    )
