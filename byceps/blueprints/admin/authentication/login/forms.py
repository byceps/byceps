"""
byceps.blueprints.admin.authentication.login.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import InputRequired

from .....util.l10n import LocalizedForm


class LogInForm(LocalizedForm):
    screen_name = StringField(lazy_gettext('Username'), [InputRequired()])
    password = PasswordField(lazy_gettext('Password'), [InputRequired()])
    permanent = BooleanField()
