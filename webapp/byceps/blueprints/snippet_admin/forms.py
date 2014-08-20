# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from wtforms import Form, TextAreaField, TextField


class CreateForm(Form):
    name = TextField('Bezeichner')
    url_path = TextField('URL-Pfad')
    title = TextField('Titel')
    body = TextAreaField('Text')


class UpdateForm(CreateForm):
    pass
