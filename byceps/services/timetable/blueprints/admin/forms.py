"""
byceps.services.timetable.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, DateTimeLocalField, StringField
from wtforms.validators import InputRequired, Length

from byceps.util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    scheduled_at = DateTimeLocalField(
        lazy_gettext('Point in time'), validators=[InputRequired()]
    )
    description = StringField(
        lazy_gettext('Description'), [InputRequired(), Length(max=200)]
    )
    location = StringField(lazy_gettext('Location'), [Length(max=40)])
    link_target = StringField(lazy_gettext('Link target'), [Length(max=80)])
    link_label = StringField(lazy_gettext('Link label'), [Length(max=80)])
    hidden = BooleanField(lazy_gettext('hidden'))


class CreateForm(_BaseForm):
    pass


class UpdateForm(_BaseForm):
    pass
