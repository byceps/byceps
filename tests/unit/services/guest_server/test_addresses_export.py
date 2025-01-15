"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
from ipaddress import IPv4Address

from byceps.services.guest_server import guest_server_export_service
from byceps.services.guest_server.models import (
    Address,
    AddressID,
    Server,
    Setting,
)

from tests.helpers import generate_uuid


def test_export_addresses_for_netbox(party, make_user, make_server):
    owner1 = make_user(screen_name='Owner A')
    owner2 = make_user(screen_name='Owner B')

    server1 = make_server(owner=owner1, approved=True)
    server1 = add_address(server1, '10.0.100.104', 'hundertvier')

    server2 = make_server(owner=owner2, approved=True)
    server2 = add_address(server2, '10.0.100.106', 'hundertsechs')
    server2 = add_address(server2, '10.0.100.107', 'hundertsieben')

    servers = [server1, server2]

    setting = Setting(
        party_id=party.id,
        netmask=None,
        gateway=None,
        dns_server1=None,
        dns_server2=None,
        domain='lan',
    )

    actual = guest_server_export_service.export_addresses_for_netbox(
        servers, setting
    )

    assert list(actual) == [
        'address,status,dns_name,description\r\n',
        '10.0.100.104/24,active,hundertvier.lan,Owner A\r\n',
        '10.0.100.106/24,active,hundertsechs.lan,Owner B\r\n',
        '10.0.100.107/24,active,hundertsieben.lan,Owner B\r\n',
    ]


def add_address(server: Server, ip_address_str: str, hostname: str) -> Server:
    address = Address(
        id=AddressID(generate_uuid()),
        server_id=server.id,
        created_at=server.created_at,
        ip_address=IPv4Address(ip_address_str),
        hostname=hostname,
        netmask=None,
        gateway=None,
    )

    addresses = server.addresses.union({address})

    return dataclasses.replace(server, addresses=addresses)
