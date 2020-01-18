"""
byceps.blueprints.admin.snippet.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, ValidationError

from ....util.l10n import LocalizedForm


class MountpointCreateForm(LocalizedForm):
    site_id = StringField('Site-ID', [InputRequired()])
    endpoint_suffix = StringField('Bezeichner', [InputRequired()])
    url_path = StringField('URL-Pfad', [InputRequired()])

    @staticmethod
    def validate_url_path(form, field):
        if not field.data.startswith('/'):
            raise ValidationError('Der URL-Pfad muss mit einem Slash beginnen.')


class MountpointUpdateForm(MountpointCreateForm):
    pass


class FragmentCreateForm(LocalizedForm):
    name = StringField('Bezeichner', [InputRequired()])
    body = TextAreaField('Text', [InputRequired()])


class FragmentUpdateForm(FragmentCreateForm):
    pass


class DocumentCreateForm(FragmentCreateForm):
    title = StringField('Titel', [InputRequired()])
    head = TextAreaField('Seitenkopf')
    image_url_path = StringField('Bild-URL-Pfad')


class DocumentUpdateForm(DocumentCreateForm):
    pass
