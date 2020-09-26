"""
byceps.blueprints.common.authentication.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import InputRequired

from ....util.l10n import LocalizedForm


class LoginForm(LocalizedForm):
    screen_name = StringField('Benutzername', [InputRequired()])
    password = PasswordField('Passwort', [InputRequired()])
    permanent = BooleanField()
