"""
byceps.blueprints.admin.user.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from ....services.site import service as site_service
from ....services.user import screen_name_validator
from ....util.l10n import LocalizedForm

from ...common.user.creation.forms import ScreenNameValidator


MINIMUM_PASSWORD_LENGTH = 10
MAXIMUM_PASSWORD_LENGTH = 100


class ChangeEmailAddressForm(LocalizedForm):
    email_address = StringField('Neue E-Mail-Adresse', [InputRequired(), Length(min=6, max=120)])
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=1000)])


class ChangeScreenNameForm(LocalizedForm):
    screen_name = StringField('Neuer Benutzername', [
        InputRequired(),
        Length(min=screen_name_validator.MIN_LENGTH,
               max=screen_name_validator.MAX_LENGTH),
        ScreenNameValidator(),
    ])
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=1000)])


class CreateAccountForm(LocalizedForm):
    screen_name = StringField('Benutzername', [
        InputRequired(),
        Length(min=screen_name_validator.MIN_LENGTH,
               max=screen_name_validator.MAX_LENGTH),
        ScreenNameValidator(),
    ])
    first_names = StringField('Vorname(n)', [InputRequired(), Length(min=2, max=40)])
    last_name = StringField('Nachname', [InputRequired(), Length(min=2, max=80)])
    email_address = StringField('E-Mail-Adresse', [InputRequired(), Length(min=6, max=120)])
    password = PasswordField('Passwort', [InputRequired(), Length(min=MINIMUM_PASSWORD_LENGTH, max=MAXIMUM_PASSWORD_LENGTH)])
    site_id = SelectField('Site-ID', validators=[Optional()])

    def set_site_choices(self):
        sites = site_service.get_all_sites()
        sites = [site for site in sites if site.enabled]
        sites.sort(key=lambda site: site.id)

        choices = [(str(site.id), site.id) for site in sites]
        choices.insert(0, ('', '<keine>'))
        self.site_id.choices = choices


class DeleteAccountForm(LocalizedForm):
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=1000)])
    verification = StringField('Bestätigung', validators=[InputRequired()])

    @staticmethod
    def validate_verification(form, field):
        if field.data != 'löschen':
            raise ValidationError('Ungültiges Bestätigungswort')


class SetPasswordForm(LocalizedForm):
    password = PasswordField('Passwort', [InputRequired(), Length(min=MINIMUM_PASSWORD_LENGTH, max=MAXIMUM_PASSWORD_LENGTH)])


class SuspendAccountForm(LocalizedForm):
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=1000)])
