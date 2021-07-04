"""
byceps.blueprints.admin.snippet.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import lazy_gettext
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, ValidationError

from ....services.site.transfer.models import Site
from ....util.l10n import LocalizedForm


class MountpointCreateForm(LocalizedForm):
    site_id = SelectField(lazy_gettext('Site'), [InputRequired()])
    endpoint_suffix = StringField(lazy_gettext('Identifier'), [InputRequired()])
    url_path = StringField(lazy_gettext('URL path'), [InputRequired()])

    def set_site_id_choices(self, sites: set[Site]) -> None:
        self.site_id.choices = [
            (site.id, site.title)
            for site in sorted(sites, key=lambda site: site.title)
        ]

    @staticmethod
    def validate_url_path(form, field):
        if not field.data.startswith('/'):
            raise ValidationError(
                lazy_gettext('URL path has to start with a slash.')
            )


class FragmentCreateForm(LocalizedForm):
    name = StringField(lazy_gettext('Name'), [InputRequired()])
    body = TextAreaField(lazy_gettext('Text'), [InputRequired()])


class FragmentUpdateForm(FragmentCreateForm):
    pass


class DocumentCreateForm(FragmentCreateForm):
    title = StringField(lazy_gettext('Title'), [InputRequired()])
    head = TextAreaField(lazy_gettext('Page header'))
    image_url_path = StringField(lazy_gettext('Image URL path'))


class DocumentUpdateForm(DocumentCreateForm):
    pass
