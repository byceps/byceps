"""
byceps.services.party.party_export_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from lanpartydb.models import Party as LpdbParty
from lanpartydb.serialization import serialize_party_to_toml

from byceps.services.brand import brand_service
from byceps.services.seating import seat_service
from byceps.services.ticketing import ticket_service

from .models import Party


def export_party_for_lanpartydb(party: Party) -> str:
    """Export party for the OrgaTalk LAN Party Database.

    The export is incomplete and contains only the data available to BYCEPS.
    """
    brand = brand_service.get_brand(party.brand_id)
    seat_count = seat_service.count_seats_for_party(party.id)
    tickets_sold_count = ticket_service.count_sold_tickets_for_party(party.id)

    lpdb_party = LpdbParty(
        slug=party.id,
        title=party.title,
        series_slug=brand.id,
        start_on=party.starts_at.date(),
        end_on=party.ends_at.date(),
        seats=seat_count,
        attendees=tickets_sold_count,
        location=None,
    )

    return serialize_party_to_toml(lpdb_party)
