"""
byceps.blueprints.admin.webhook.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, StringField
from wtforms.validators import InputRequired, Optional

from byceps.announce.events import EVENT_TYPES_TO_NAMES
from byceps.util.forms import MultiCheckboxField
from byceps.util.l10n import LocalizedForm


def _get_event_type_choices() -> list[tuple[str, str]]:
    event_names = EVENT_TYPES_TO_NAMES.values()
    return [(event_name, event_name) for event_name in sorted(event_names)]


class _BaseForm(LocalizedForm):
    description = StringField(lazy_gettext('Description'), [InputRequired()])
    format = StringField(lazy_gettext('Format'), [InputRequired()])
    url = StringField(lazy_gettext('URL'), [InputRequired()])
    event_types = MultiCheckboxField(
        lazy_gettext('Event types'),
        choices=_get_event_type_choices(),
        validators=[InputRequired()],
    )


class CreateForm(_BaseForm):
    pass


class UpdateForm(_BaseForm):
    text_prefix = StringField(lazy_gettext('Text prefix'), [Optional()])
    extra_fields = StringField(lazy_gettext('Additional fields'), [Optional()])
    enabled = BooleanField(lazy_gettext('Enabled'))
