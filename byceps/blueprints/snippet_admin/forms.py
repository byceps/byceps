"""
byceps.blueprints.snippet_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import StringField, TextAreaField

from ...util.l10n import LocalizedForm


class MountpointCreateForm(LocalizedForm):
    endpoint_suffix = StringField('Bezeichner')
    url_path = StringField('URL-Pfad')


class MountpointUpdateForm(MountpointCreateForm):
    pass


class FragmentCreateForm(LocalizedForm):
    name = StringField('Bezeichner')
    body = TextAreaField('Text')


class FragmentUpdateForm(FragmentCreateForm):
    pass


class DocumentCreateForm(FragmentCreateForm):
    title = StringField('Titel')
    head = TextAreaField('Seitenkopf')
    image_url_path = StringField('Bild-URL-Pfad')


class DocumentUpdateForm(DocumentCreateForm):
    pass
