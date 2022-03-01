"""
byceps.blueprints.admin.snippet.mountpoint.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import lazy_gettext
from wtforms import SelectField, StringField
from wtforms.validators import InputRequired, ValidationError

from .....services.site.transfer.models import Site
from .....util.l10n import LocalizedForm


class SiteSelectForm(LocalizedForm):
    site_id = SelectField(lazy_gettext('Site'), [InputRequired()])

    def set_site_id_choices(self, sites: set[Site]) -> None:
        self.site_id.choices = [
            (site.id, site.title)
            for site in sorted(sites, key=lambda site: site.title)
        ]


class CreateForm(LocalizedForm):
    endpoint_suffix = StringField(lazy_gettext('Identifier'), [InputRequired()])
    url_path = StringField(lazy_gettext('URL path'), [InputRequired()])

    @staticmethod
    def validate_url_path(form, field):
        if not field.data.startswith('/'):
            raise ValidationError(
                lazy_gettext('URL path has to start with a slash.')
            )
