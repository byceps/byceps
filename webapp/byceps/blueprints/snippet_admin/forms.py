# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from wtforms import SelectField, StringField, TextAreaField

from ...util.l10n import LocalizedForm


class MountpointCreateForm(LocalizedForm):
    endpoint_suffix = StringField('Bezeichner')
    url_path = StringField('URL-Pfad')
    snippet_id = SelectField('Snippet')


class MountpointUpdateForm(MountpointCreateForm):
    pass


class SnippetCreateForm(LocalizedForm):
    name = StringField('Bezeichner')
    title = StringField('Titel')
    body = TextAreaField('Text')


class SnippetUpdateForm(SnippetCreateForm):
    pass
