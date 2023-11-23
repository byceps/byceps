"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.events.authn import UserIdentityTagCreatedEvent
from byceps.services.authn.identity_tag import authn_identity_tag_domain_service


def test_create_tag(user, admin_user):
    initiator = admin_user
    identifier = '0001234567'
    note = 'Handed out on 2023-09-30'

    tag, event, log_entry = authn_identity_tag_domain_service.create_tag(
        initiator, identifier, user, note=note
    )

    assert tag.id is not None
    assert tag.created_at is not None
    assert tag.creator == initiator
    assert tag.identifier == identifier
    assert tag.user == user
    assert tag.note == note
    assert not tag.suspended

    assert event.__class__ is UserIdentityTagCreatedEvent
    assert event.occurred_at == tag.created_at
    assert event.initiator == initiator
    assert event.identifier == identifier
    assert event.user == user

    assert log_entry.id is not None
    assert log_entry.occurred_at == tag.created_at
    assert log_entry.event_type == 'user-identity-tag-created'
    assert log_entry.user_id == user.id
    assert log_entry.initiator_id == initiator.id
    assert log_entry.data == {'tag_id': str(tag.id)}
