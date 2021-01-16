"""
byceps.blueprints.common.authentication.login.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import InputRequired

from .....util.l10n import LocalizedForm


class LoginForm(LocalizedForm):
    screen_name = StringField('Benutzername', [InputRequired()])
    password = PasswordField('Passwort', [InputRequired()])
    permanent = BooleanField()
