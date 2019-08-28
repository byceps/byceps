"""
byceps.blueprints.admin.user.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import PasswordField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError

from ....services.user import screen_name_validator
from ....util.l10n import LocalizedForm

from ...user.creation.forms import ScreenNameValidator


MINIMUM_PASSWORD_LENGTH = 10
MAXIMUM_PASSWORD_LENGTH = 100


class ChangeScreenNameForm(LocalizedForm):
    screen_name = StringField('Neuer Benutzername', [
        InputRequired(),
        Length(min=screen_name_validator.MIN_LENGTH,
               max=screen_name_validator.MAX_LENGTH),
        ScreenNameValidator(),
    ])
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=400)])


class CreateAccountForm(LocalizedForm):
    screen_name = StringField('Benutzername', [
        InputRequired(),
        Length(min=screen_name_validator.MIN_LENGTH,
               max=screen_name_validator.MAX_LENGTH),
        ScreenNameValidator(),
    ])
    first_names = StringField('Vorname(n)', [InputRequired(), Length(min=2, max=40)])
    last_name = StringField('Nachname', [InputRequired(), Length(min=2, max=40)])
    email_address = StringField('E-Mail-Adresse', [InputRequired(), Length(min=6)])
    password = PasswordField('Passwort', [InputRequired(), Length(min=MINIMUM_PASSWORD_LENGTH, max=MAXIMUM_PASSWORD_LENGTH)])


class DeleteAccountForm(LocalizedForm):
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=400)])
    verification = StringField('Bestätigung', validators=[InputRequired()])

    def validate_verification(form, field):
        if field.data != 'löschen':
            raise ValidationError('Ungültiges Bestätigungswort')


class SetPasswordForm(LocalizedForm):
    password = PasswordField('Passwort', [InputRequired(), Length(min=MINIMUM_PASSWORD_LENGTH, max=MAXIMUM_PASSWORD_LENGTH)])


class SuspendAccountForm(LocalizedForm):
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=400)])
