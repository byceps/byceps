"""
byceps.services.ticketing.blueprints.site.intranet_login_as_checkin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a user logs in to a site with the check-in-on-login flag set, check
in their ticket.

This is useful for a party's intranet site when the party has no
check-in at the door.

:Copyright: 2014-2025 Jochen Kupperschmidt
"""

from byceps.services.authn.events import UserLoggedInEvent
from byceps.services.authn.signals import user_logged_in
from byceps.services.party.models import PartyID
from byceps.services.site import site_service
from byceps.services.ticketing import (
    ticket_service,
    ticket_user_checkin_service,
)
from byceps.services.user.models.user import User
from byceps.util.jobqueue import enqueue


@user_logged_in.connect
def _on_user_logged_in(sender, *, event: UserLoggedInEvent) -> None:
    if event.site is None:
        return

    user = event.initiator
    site = site_service.get_site(event.site.id)

    if site.party_id and site.check_in_on_login:
        enqueue(_check_in_users_tickets, user, site.party_id)


def _check_in_users_tickets(user: User, party_id: PartyID) -> None:
    """Find the user's tickets used for the party and check them in."""
    tickets = ticket_service.get_tickets_used_by_user(user.id, party_id)

    for ticket in tickets:
        ticket_user_checkin_service.check_in_user(party_id, ticket.id, user)
