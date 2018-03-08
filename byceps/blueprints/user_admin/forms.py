"""
byceps.blueprints.user_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import PasswordField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError

from ...util.l10n import LocalizedForm


class DeleteAccountForm(LocalizedForm):
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=400)])
    verification = StringField('Bestätigung', validators=[InputRequired()])

    def validate_verification(form, field):
        if field.data != 'löschen':
            raise ValidationError('Ungültiges Bestätigungswort')


class SetPasswordForm(LocalizedForm):
    password = PasswordField('Passwort', [InputRequired(), Length(min=8)])


class SuspendAccountForm(LocalizedForm):
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=400)])
