"""
byceps.blueprints.common.guest_server.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterable

from flask import abort, g
import qrcode
from qrcode.image.svg import SvgPathImage

from byceps.services.guest_server import guest_server_service
from byceps.services.guest_server.models import Address, Server
from byceps.services.party import party_service, party_setting_service
from byceps.services.site import site_service
from byceps.services.site.models import SiteID
from byceps.services.user import user_service
from byceps.typing import PartyID
from byceps.util.authorization import has_current_user_permission
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import login_required


blueprint = create_blueprint('guest_server_common', __name__)


@blueprint.get('/guest_servers/<uuid:server_id>/printable_card.html')
@login_required
@templated
def view_printable_card(server_id):
    """Show a printable card for the server."""
    server = _get_server_or_404(server_id)
    party = party_service.get_party(server.party_id)

    _ensure_user_allowed_to_view_printable_card(server)

    owner = user_service.get_user(server.owner_id)
    addresses = _sort_addresses(server.addresses)
    setting = guest_server_service.get_setting_for_party(party.id)

    site_server_name = _get_site_server_name(party.id)
    qrcode_data = (
        f'https://{site_server_name}/guest_servers/servers/{server.id}/admin'
    )
    qrcode_svg = _generate_qrcode_svg(qrcode_data)
    qrcode_svg_inline = _inline_svg(qrcode_svg)

    return {
        'party_title': party.title,
        'owner': owner,
        'addresses': addresses,
        'domain': setting.domain,
        'qrcode': qrcode_svg_inline,
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


def _get_site_server_name(party_id: PartyID) -> str:
    """Return the server name of the party's primary site."""
    primary_party_site_id = party_setting_service.find_setting_value(
        party_id, 'primary_party_site_id'
    )
    if not primary_party_site_id:
        abort(500, 'Primary party site ID not configured.')

    site = site_service.get_site(SiteID(primary_party_site_id))
    return site.server_name


def _generate_qrcode_svg(data: str) -> str:
    """Generate QR code as SVG."""
    image = qrcode.make(data, border=0, box_size=10, image_factory=SvgPathImage)
    return image.to_string().decode('utf-8')


def _inline_svg(svg: str) -> str:
    """Encode SVG to be used inline as part of a data URI.

    Replacements are not complete, but sufficient for this case.

    See https://codepen.io/tigt/post/optimizing-svgs-in-data-uris
    for details.
    """
    replaced = (
        svg
        .replace('\n', '%0A')
        .replace('#', '%23')
        .replace('<', '%3C')
        .replace('>', '%3E')
        .replace('"', "'")
    )

    return 'data:image/svg+xml,' + replaced
