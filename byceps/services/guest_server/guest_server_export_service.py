"""
byceps.services.guest_server.guest_server_export_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator

from byceps.services.guest_server.models import Address, Server, Setting
from byceps.services.user.models.user import User
from byceps.util.export import serialize_tuples_to_csv


def export_addresses_for_netbox(
    servers: list[Server], setting: Setting
) -> Iterator[str]:
    """Export addresses for a party as NetBox-compatible CSV.

    Suitable for importing into NetBox
    (https://github.com/netbox-community/netbox).
    """
    # field names as defined by NetBox
    header_row = ('address', 'status', 'dns_name', 'description')

    body_rows = list(_generate_body_rows(servers, setting))
    body_rows.sort()

    rows = [header_row] + body_rows

    return serialize_tuples_to_csv(rows)


def _generate_body_rows(
    servers: list[Server], setting: Setting
) -> Iterator[tuple[str, str, str, str]]:
    for owner, address in _get_owners_and_addresses(servers):
        if address.ip_address and address.hostname:
            address_str = f'{str(address.ip_address)}/24'
            status = 'active'
            hostname = address.hostname
            if setting.domain:
                hostname += '.' + setting.domain
            owner_name = owner.screen_name or 'unknown'

            yield address_str, status, hostname, owner_name


def _get_owners_and_addresses(
    servers: list[Server],
) -> Iterator[tuple[User, Address]]:
    approved_servers = [server for server in servers if server.approved]

    for server in approved_servers:
        for address in server.addresses:
            yield server.owner, address
