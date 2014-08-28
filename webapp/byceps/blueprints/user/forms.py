# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from wtforms import BooleanField, FileField, Form, PasswordField, TextField
from wtforms.validators import Required


class CreateForm(Form):
    screen_name = TextField('Benutzername', validators=[Required()])
    email_address = TextField('E-Mail-Adresse', validators=[Required()])
    password = PasswordField('Passwort', validators=[Required()])
    consent_to_terms = BooleanField('AGB', validators=[Required()])


class AvatarImageUpdateForm(Form):
    image = FileField('Bilddatei')


class LoginForm(Form):
    screen_name = TextField('Benutzername', validators=[Required()])
    password = PasswordField('Passwort', validators=[Required()])
