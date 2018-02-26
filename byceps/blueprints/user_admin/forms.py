"""
byceps.blueprints.user_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import PasswordField, TextAreaField
from wtforms.validators import InputRequired, Length

from ...util.l10n import LocalizedForm


class SetPasswordForm(LocalizedForm):
    password = PasswordField('Passwort', [InputRequired(), Length(min=8)])


class SuspendAccountForm(LocalizedForm):
    reason = TextAreaField('Begründung', validators=[InputRequired(), Length(max=200)])
