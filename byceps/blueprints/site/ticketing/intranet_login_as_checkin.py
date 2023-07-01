"""
byceps.blueprints.site.ticketing.intranet_login_as_checkin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a user logs in to a site with the check-in-on-login flag set, check
in their ticket.

This is useful for a party's intranet site when they don't have a
check-in at the door.

:Copyright: 2014-2023 Jochen Kupperschmidt
"""

from byceps.events.auth import UserLoggedInEvent
from byceps.services.site import site_service
from byceps.services.ticketing import (
    ticket_service,
    ticket_user_checkin_service,
)
from byceps.signals.auth import user_logged_in
from byceps.typing import PartyID, UserID
from byceps.util.jobqueue import enqueue


@user_logged_in.connect
def _on_user_logged_in(sender, *, event: UserLoggedInEvent) -> None:
    if event.site_id is None:
        return

    site = site_service.get_site(event.site_id)

    if site.party_id and site.check_in_on_login:
        enqueue(_check_in_users_tickets, event.initiator_id, site.party_id)


def _check_in_users_tickets(user_id: UserID, party_id: PartyID) -> None:
    """Find the user's tickets used for the party and check them in."""
    tickets = ticket_service.get_tickets_used_by_user(user_id, party_id)

    for ticket in tickets:
        ticket_user_checkin_service.check_in_user(party_id, ticket.id, user_id)
