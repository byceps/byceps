"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ipaddress import IPv4Address

from byceps.services.guest_server import guest_server_domain_service
from byceps.services.guest_server.models import AddressData


def test_register_server(party, admin_user, user):
    owner = user
    address_datas = {
        AddressData(
            ip_address=IPv4Address('10.0.100.104'),
            hostname='bluebox',
            netmask=IPv4Address('255.255.255.0'),
            gateway=IPv4Address('10.0.100.1'),
        ),
    }

    server, event = guest_server_domain_service.register_server(
        party,
        admin_user,
        owner,
        address_datas,
        description='2U, spray-painted in pink',
        notes_owner='I need two ports.',
        notes_admin='Request denied.',
    )

    assert server.id is not None
    assert server.party_id == party.id
    assert server.created_at is not None
    assert server.creator.id == admin_user.id
    assert server.owner.id == owner.id
    assert server.description == '2U, spray-painted in pink'
    assert server.notes_owner == 'I need two ports.'
    assert server.notes_admin == 'Request denied.'
    assert not server.approved

    assert len(server.addresses) == 1
    address = list(server.addresses)[0]
    assert address.id is not None
    assert address.server_id == server.id
    assert address.created_at == server.created_at
    assert address.ip_address == IPv4Address('10.0.100.104')
    assert address.hostname == 'bluebox'
    assert address.netmask == IPv4Address('255.255.255.0')
    assert address.gateway == IPv4Address('10.0.100.1')

    assert event.occurred_at == server.created_at
    assert event.initiator_id == admin_user.id
    assert event.initiator_screen_name == admin_user.screen_name
    assert event.party_id == party.id
    assert event.party_title == party.title
    assert event.owner_id == owner.id
    assert event.owner_screen_name == owner.screen_name
    assert event.server_id == server.id
