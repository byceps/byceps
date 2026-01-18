"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.services.authn.events import UserIdentityTagDeletedEvent
from byceps.services.authn.identity_tag import authn_identity_tag_domain_service
from byceps.services.authn.identity_tag.models import UserIdentityTag
from byceps.services.user.models.user import User

from tests.helpers import generate_token, generate_uuid


def test_delete_tag(tag: UserIdentityTag, user: User, admin_user: User):
    initiator = admin_user

    event, log_entry = authn_identity_tag_domain_service.delete_tag(
        tag, initiator
    )

    assert event.__class__ is UserIdentityTagDeletedEvent
    assert event.occurred_at is not None
    assert event.initiator is not None
    assert event.initiator.id == initiator.id
    assert event.initiator.screen_name == initiator.screen_name
    assert event.identifier == tag.identifier
    assert event.user.id == user.id
    assert event.user.screen_name == user.screen_name

    assert log_entry.id is not None
    assert log_entry.occurred_at == event.occurred_at
    assert log_entry.event_type == 'user-identity-tag-deleted'
    assert log_entry.user == user
    assert log_entry.initiator == initiator
    assert log_entry.data == {'tag_id': str(tag.id)}


@pytest.fixture
def tag(make_user, user: User, admin_user: User):
    return UserIdentityTag(
        id=generate_uuid(),
        created_at=datetime.utcnow(),
        creator=admin_user,
        identifier=generate_token(),
        user=user,
        note=None,
        suspended=False,
    )
