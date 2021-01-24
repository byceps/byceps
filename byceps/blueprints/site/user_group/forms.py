"""
byceps.blueprints.site.user_group.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField, TextAreaField

from ....util.l10n import LocalizedForm


class CreateForm(LocalizedForm):
    title = StringField(lazy_gettext('Titel'))
    description = TextAreaField(lazy_gettext('Beschreibung'))
