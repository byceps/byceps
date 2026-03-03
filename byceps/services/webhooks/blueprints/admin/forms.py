"""
byceps.services.webhooks.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import InputRequired, Optional

from byceps.announce.announce import get_event_names
from byceps.services.webhooks.models import (
    get_outgoing_webhook_format_label,
    OutgoingWebhookFormat,
)
from byceps.util.forms import MultiCheckboxField
from byceps.util.l10n import LocalizedForm


def _get_event_type_choices() -> list[tuple[str, str]]:
    event_names = get_event_names()
    return [(event_name, event_name) for event_name in sorted(event_names)]


class _BaseForm(LocalizedForm):
    description = StringField(lazy_gettext('Description'), [InputRequired()])
    format = SelectField(lazy_gettext('Format'), [InputRequired()])
    url = StringField(lazy_gettext('URL'), [InputRequired()])
    event_types = MultiCheckboxField(
        lazy_gettext('Event types'),
        choices=_get_event_type_choices(),
        validators=[InputRequired()],
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_format_choices()

    def set_format_choices(self) -> None:
        choices = [
            (format.name, get_outgoing_webhook_format_label(format))
            for format in OutgoingWebhookFormat
        ]
        choices.sort(key=lambda choice: choice[1])
        choices.insert(0, ('', '<' + lazy_gettext('choose') + '>'))

        self.format.choices = choices


class CreateForm(_BaseForm):
    pass


class UpdateForm(_BaseForm):
    text_prefix = StringField(lazy_gettext('Text prefix'), [Optional()])
    extra_fields = StringField(lazy_gettext('Additional fields'), [Optional()])
    enabled = BooleanField(lazy_gettext('Enabled'))
