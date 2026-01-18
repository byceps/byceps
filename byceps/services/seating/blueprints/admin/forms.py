"""
byceps.services.seating.blueprints.admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import DateTimeLocalField, IntegerField, SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional

from byceps.services.seating.models import SeatGroup
from byceps.services.ticketing import ticket_bundle_service
from byceps.services.ticketing.models.ticket import TicketBundle
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


class SeatGroupOccupyForm(LocalizedForm):
    ticket_bundle_id = SelectField(
        lazy_gettext('Ticket bundle'), [InputRequired()]
    )

    def set_ticket_bundle_id_choices(self, group: SeatGroup) -> None:
        def get_label(bundle: TicketBundle) -> str:
            bundle_title = bundle.label or lazy_gettext('unnamed')
            ticket_category_title_label = lazy_gettext('category')
            ticket_category_title = bundle.ticket_category.title
            ticket_quantity_label = lazy_gettext('tickets')
            ticket_quantity = bundle.ticket_quantity
            bundle_id_label = lazy_gettext('ID')
            bundle_id = str(bundle.id)

            return (
                f'{bundle_title} ('
                f'{ticket_category_title_label}: {ticket_category_title}, '
                f'{ticket_quantity} {ticket_quantity_label}, '
                f'{bundle_id_label}: {bundle_id})'
            )

        bundles = _get_matching_ticket_bundles(group)

        choices = [(str(bundle.id), get_label(bundle)) for bundle in bundles]
        choices.sort(key=lambda choice: choice[1])
        choices.insert(0, ('', '<' + lazy_gettext('choose') + '>'))

        self.ticket_bundle_id.choices = choices


def _get_matching_ticket_bundles(group: SeatGroup) -> list[TicketBundle]:
    bundles = ticket_bundle_service.get_bundles_for_party(group.party_id)
    return [bundle for bundle in bundles if _is_matching_bundle(bundle, group)]


def _is_matching_bundle(bundle: TicketBundle, group: SeatGroup) -> bool:
    return (
        not bundle.occupies_seat_group
        and bundle.ticket_category.id == group.ticket_category_id
        and bundle.ticket_quantity == group.seat_quantity
    )


class ReservationPreconditionCreateForm(LocalizedForm):
    at_earliest = DateTimeLocalField(
        lazy_gettext('At earliest'), validators=[InputRequired()]
    )
    minimum_ticket_quantity = IntegerField(
        lazy_gettext('Minimum number of tickets'), validators=[InputRequired()]
    )
