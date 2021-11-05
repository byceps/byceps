"""
byceps.blueprints.common.guest_server.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Iterable

from flask import abort, g

from ....services.guest_server import service as guest_server_service
from ....services.guest_server.transfer.models import Address, Server
from ....services.party import service as party_service
from ....services.user import service as user_service
from ....util.authorization import has_current_user_permission
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import login_required


blueprint = create_blueprint('guest_server_common', __name__)


@blueprint.get('/guest_servers/<uuid:server_id>/printable_card.html')
@login_required
@templated
def view_printable_card(server_id):
    """Show a printable card for the server."""
    server = _get_server_or_404(server_id)
    party = party_service.get_party(server.party_id)

    owner = user_service.get_user(server.owner_id)

    _ensure_user_allowed_to_view_printable_card(server)

    addresses = _sort_addresses(server.addresses)

    return {
        'party_title': party.title,
        'owner': owner,
        'addresses': addresses,
    }


def _get_server_or_404(server_id) -> Server:
    server = guest_server_service.find_server(server_id)

    if server is None:
        abort(404)

    return server


def _ensure_user_allowed_to_view_printable_card(server: Server) -> None:
    """Abort if the current user is not allowed to view the printable
    card for that server.
    """
    if g.user.id != server.owner_id and not has_current_user_permission(
        'guest_server.administrate'
    ):
        abort(404)


def _sort_addresses(addresses: Iterable[Address]) -> list[Address]:
    """Sort addresses.

    By IP address first, hostname second. `None` at the end.
    """
    return list(
        sorted(
            addresses,
            key=lambda addr: (
                addr.ip_address is None,
                addr.ip_address,
                addr.hostname is None,
                addr.hostname,
            ),
        )
    )
