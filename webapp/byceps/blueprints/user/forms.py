# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from wtforms import BooleanField, FileField, PasswordField, StringField
from wtforms.validators import DataRequired

from ...util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    screen_name = StringField('Benutzername', validators=[DataRequired()])
    email_address = StringField('E-Mail-Adresse', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    consent_to_terms = BooleanField('AGB', validators=[DataRequired()])


class AvatarImageUpdateForm(LocalizedForm):
    image = FileField('Bilddatei')


class LoginForm(LocalizedForm):
    screen_name = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
