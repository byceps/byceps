# -*- coding: utf-8 -*-

"""
byceps.blueprints.authentication.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import DataRequired

from ...util.l10n import LocalizedForm


class LoginForm(LocalizedForm):
    screen_name = StringField('Benutzername', [DataRequired()])
    password = PasswordField('Passwort', [DataRequired()])
    permanent = BooleanField()
