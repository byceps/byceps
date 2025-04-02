"""
byceps.services.authn.login.blueprints.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import InputRequired

from byceps.util.l10n import LocalizedForm


class LogInForm(LocalizedForm):
    username = StringField(lazy_gettext('Username'), [InputRequired()])
    password = PasswordField(lazy_gettext('Password'), [InputRequired()])
    permanent = BooleanField()
