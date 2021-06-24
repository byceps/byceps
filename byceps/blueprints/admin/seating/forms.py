"""
byceps.blueprints.admin.seating.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired, Length

from ....util.l10n import LocalizedForm


class AreaCreateForm(LocalizedForm):
    slug = StringField(
        lazy_gettext('Slug'),
        validators=[InputRequired(), Length(min=1, max=20)],
    )
    title = StringField(
        lazy_gettext('Title'),
        validators=[InputRequired(), Length(min=1, max=40)],
    )
