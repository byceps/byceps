"""
byceps.services.party.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext, lazy_gettext, lazy_pgettext
from wtforms import BooleanField, DateTimeLocalField, IntegerField, StringField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from byceps.services.party import party_service
from byceps.util.l10n import LocalizedForm


class _BaseForm(LocalizedForm):
    title = StringField(
        lazy_gettext('Title'),
        validators=[InputRequired(), Length(min=1, max=40)],
    )
    starts_at = DateTimeLocalField(
        lazy_gettext('Start'), validators=[InputRequired()]
    )
    ends_at = DateTimeLocalField(
        lazy_gettext('End'), validators=[InputRequired()]
    )
    max_ticket_quantity = IntegerField(
        lazy_gettext('Maximum number of tickets'), validators=[Optional()]
    )

    @staticmethod
    def validate_ends_at(form, field):
        """Ensure that the party starts before it ends."""
        if form.starts_at.data >= form.ends_at.data:
            raise ValidationError(
                gettext('Start value must be before end value.')
            )


class CreateForm(_BaseForm):
    id = StringField(
        lazy_gettext('ID'), validators=[InputRequired(), Length(min=1, max=40)]
    )

    @staticmethod
    def validate_id(form, field):
        party_id = field.data
        if party_service.find_party(party_id) is not None:
            raise ValidationError(lazy_gettext('The value is already in use.'))


class UpdateForm(_BaseForm):
    ticket_management_enabled = BooleanField(
        lazy_gettext('Ticket management open')
    )
    seat_management_enabled = BooleanField(lazy_gettext('Seat management open'))
    hidden = BooleanField(lazy_gettext('hidden'))
    canceled = BooleanField(lazy_pgettext('party', 'canceled'))
    archived = BooleanField(lazy_gettext('archived'))
