"""
byceps.services.user_group.blueprints.site.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from byceps.services.party.models import PartyID
from byceps.services.user_group import user_group_service
from byceps.util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'), [InputRequired(), Length(max=40)]
    )
    description = TextAreaField(
        lazy_gettext('Description'), [Optional(), Length(max=200)]
    )


class CreateForm(_BaseForm):
    def __init__(self, party_id: PartyID, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._party_id = party_id

    @staticmethod
    def validate_title(form, field):
        title = field.data.strip()

        if not user_group_service.is_title_available(form._party_id, title):
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
            )


class UpdateForm(_BaseForm):
    def __init__(self, party_id: PartyID, current_title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._party_id = party_id
        self._current_title = current_title

    @staticmethod
    def validate_title(form, field):
        title = field.data.strip()

        if (
            title != form._current_title
            and not user_group_service.is_title_available(form._party_id, title)
        ):
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
            )
