"""
byceps.services.ticketing.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from byceps.services.party.models import PartyID
from byceps.services.ticketing import ticket_code_service, ticket_service
from byceps.util.forms import UserScreenNameField
from byceps.util.l10n import LocalizedForm


class UpdateCodeForm(LocalizedForm):
    code = StringField(lazy_gettext('Code'), [InputRequired()])

    def __init__(self, party_id: PartyID, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._party_id = party_id

    @staticmethod
    def validate_code(form, field):
        ticket_code = field.data

        if not ticket_code_service.is_ticket_code_wellformed(ticket_code):
            raise ValidationError(lazy_gettext('Invalid format'))

        if ticket_service.find_ticket_by_code(form._party_id, ticket_code):
            raise ValidationError(lazy_gettext('The value is already in use.'))


class SpecifyUserForm(LocalizedForm):
    user = UserScreenNameField(lazy_gettext('Username'), [InputRequired()])
