"""
byceps.blueprints.admin.seating.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import IntegerField, StringField
from wtforms.validators import InputRequired, Length, Optional

from byceps.util.l10n import LocalizedForm


class _AreaFormBase(LocalizedForm):
    slug = StringField(
        lazy_gettext('Slug'),
        validators=[InputRequired(), Length(min=1, max=20)],
    )
    title = StringField(
        lazy_gettext('Title'),
        validators=[InputRequired(), Length(min=1, max=40)],
    )
    image_filename = StringField(
        lazy_gettext('Background image filename'), validators=[Optional()]
    )
    image_width = IntegerField(lazy_gettext('Width'), validators=[Optional()])
    image_height = IntegerField(lazy_gettext('Height'), validators=[Optional()])


class AreaCreateForm(_AreaFormBase):
    pass


class AreaUpdateForm(_AreaFormBase):
    pass
