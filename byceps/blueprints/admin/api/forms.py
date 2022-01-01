"""
byceps.blueprints.admin.api.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import lazy_gettext
from wtforms import SelectMultipleField, StringField
from wtforms.validators import InputRequired, Optional
from wtforms.widgets import CheckboxInput, ListWidget

from ....util.authorization import permission_registry
from ....util.l10n import LocalizedForm


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


def _get_permission_choices() -> list[tuple[str, str]]:
    permissions = permission_registry.get_registered_permissions()
    return [
        (str(permission.id), f'{permission.id} ({permission.title})')
        for permission in sorted(permissions, key=lambda p: p.id)
    ]


class CreateForm(LocalizedForm):
    permissions = MultiCheckboxField(
        lazy_gettext('Permissions'),
        choices=_get_permission_choices(),
        validators=[InputRequired()],
    )
    description = StringField(
        lazy_gettext('Description'), validators=[Optional()]
    )
