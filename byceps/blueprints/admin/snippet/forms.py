"""
byceps.blueprints.admin.snippet.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, ValidationError

from ....util.l10n import LocalizedForm


class MountpointCreateForm(LocalizedForm):
    site_id = StringField(lazy_gettext('Site-ID'), [InputRequired()])
    endpoint_suffix = StringField(lazy_gettext('Bezeichner'), [InputRequired()])
    url_path = StringField(lazy_gettext('URL-Pfad'), [InputRequired()])

    @staticmethod
    def validate_url_path(form, field):
        if not field.data.startswith('/'):
            raise ValidationError(
                lazy_gettext('Der URL-Pfad muss mit einem Slash beginnen.')
            )


class MountpointUpdateForm(MountpointCreateForm):
    pass


class FragmentCreateForm(LocalizedForm):
    name = StringField(lazy_gettext('Bezeichner'), [InputRequired()])
    body = TextAreaField(lazy_gettext('Text'), [InputRequired()])


class FragmentUpdateForm(FragmentCreateForm):
    pass


class DocumentCreateForm(FragmentCreateForm):
    title = StringField(lazy_gettext('Titel'), [InputRequired()])
    head = TextAreaField(lazy_gettext('Seitenkopf'))
    image_url_path = StringField(lazy_gettext('Bild-URL-Pfad'))


class DocumentUpdateForm(DocumentCreateForm):
    pass
