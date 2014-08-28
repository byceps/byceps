# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from wtforms import StringField, TextAreaField

from ...util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    name = StringField('Bezeichner')
    url_path = StringField('URL-Pfad')
    title = StringField('Titel')
    body = TextAreaField('Text')


class UpdateForm(CreateForm):
    pass
