"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from ipaddress import IPv4Address

import pytest

from byceps.services.guest_server import guest_server_domain_service
from byceps.services.party.models import Party
from byceps.services.user.models.user import User
from byceps.typing import BrandID, PartyID, UserID

from tests.helpers import generate_token, generate_uuid


def test_create_server(party, admin, owner):
    server, event = guest_server_domain_service.create_server(
        party,
        admin,
        owner,
        notes_owner='I need two ports.',
        notes_admin='Request denied.',
        ip_address=IPv4Address('10.0.100.104'),
        hostname='bluebox',
        netmask=IPv4Address('255.255.255.0'),
        gateway=IPv4Address('10.0.100.1'),
    )

    assert server.id is not None
    assert server.party_id == party.id
    assert server.created_at is not None
    assert server.creator_id == admin.id
    assert server.owner_id == owner.id
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
    assert event.initiator_id == admin.id
    assert event.initiator_screen_name == admin.screen_name
    assert event.party_id == party.id
    assert event.party_title == party.title
    assert event.owner_id == owner.id
    assert event.owner_screen_name == owner.screen_name
    assert event.server_id == server.id


@pytest.fixture()
def party() -> Party:
    return Party(
        PartyID(generate_token()),
        BrandID(generate_token()),
        generate_token(),
        datetime.utcnow(),
        datetime.utcnow(),
        0,
        False,
        False,
        False,
        False,
    )


@pytest.fixture(scope='module')
def build_user():
    def _wrapper(*, suspended=False, deleted=False) -> User:
        return User(
            id=UserID(generate_uuid()),
            screen_name=None,
            suspended=suspended,
            deleted=deleted,
            locale=None,
            avatar_url=None,
        )

    return _wrapper


@pytest.fixture()
def admin(build_user):
    return build_user()


@pytest.fixture()
def owner(build_user):
    return build_user()
