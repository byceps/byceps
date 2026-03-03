"""
byceps.services.ticketing.category.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired, Length, ValidationError

from byceps.services.party.models import PartyID
from byceps.services.ticketing import ticket_category_service
from byceps.util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'),
        validators=[InputRequired(), Length(min=1, max=40)],
    )


class CreateForm(_BaseForm):
    def __init__(self, party_id: PartyID, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._party_id = party_id

    @staticmethod
    def validate_title(form, field):
        title = field.data.strip()

        if ticket_category_service.find_category_by_title(
            form._party_id, title
        ):
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
            and ticket_category_service.find_category_by_title(
                form._party_id, title
            )
        ):
            raise ValidationError(
                lazy_gettext(
                    'This value is not available. Please choose another.'
                )
            )
