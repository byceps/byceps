# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from wtforms import BooleanField, FileField, PasswordField, StringField
from wtforms.validators import Required

from ...util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    screen_name = StringField('Benutzername', validators=[Required()])
    email_address = StringField('E-Mail-Adresse', validators=[Required()])
    password = PasswordField('Passwort', validators=[Required()])
    consent_to_terms = BooleanField('AGB', validators=[Required()])


class AvatarImageUpdateForm(LocalizedForm):
    image = FileField('Bilddatei')


class LoginForm(LocalizedForm):
    screen_name = StringField('Benutzername', validators=[Required()])
    password = PasswordField('Passwort', validators=[Required()])
