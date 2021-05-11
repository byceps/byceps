"""
byceps.blueprints.admin.webhook.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import lazy_gettext
from wtforms import BooleanField, StringField
from wtforms.validators import InputRequired

from ....util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    description = StringField(lazy_gettext('Description'), [InputRequired()])
    format = StringField(lazy_gettext('Format'), [InputRequired()])
    url = StringField(lazy_gettext('URL'), [InputRequired()])


class CreateForm(_BaseForm):
    pass


class UpdateForm(_BaseForm):
    text_prefix = StringField(lazy_gettext('Text prefix'), [InputRequired()])
    enabled = BooleanField(lazy_gettext('Enabled'))


def assemble_create_form(event_names: set[str]) -> type[LocalizedForm]:
    return _extend_form_for_event_types(CreateForm, event_names)


def assemble_update_form(event_names: set[str]) -> type[LocalizedForm]:
    return _extend_form_for_event_types(UpdateForm, event_names)


def _extend_form_for_event_types(
    form_class,
    event_names: set[str],
) -> type[LocalizedForm]:
    """Dynamically add a checkbox per event type to the form."""

    class FormWithEventTypes(form_class):
        pass

    _add_event_field_getter_to_form(FormWithEventTypes)
    _add_event_fields_to_form(FormWithEventTypes, event_names)

    return FormWithEventTypes


def _add_event_field_getter_to_form(form_class) -> None:
    def get_field_for_event_name(self, event_name: str):
        field_name = _create_event_field_name(event_name)
        return getattr(self, field_name)

    form_class.get_field_for_event_name = get_field_for_event_name


def _add_event_fields_to_form(form_class, event_names: set[str]) -> None:
    for event_name in event_names:
        field_name = _create_event_field_name(event_name)
        field = BooleanField()
        setattr(form_class, field_name, field)


def _create_event_field_name(event_name: str) -> str:
    return f'event_{event_name}'
