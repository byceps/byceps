"""
:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.services.core.events import EventUser
from byceps.services.whereabouts import whereabouts_client_domain_service
from byceps.services.whereabouts.events import (
    WhereaboutsClientApprovedEvent,
    WhereaboutsClientRegisteredEvent,
    WhereaboutsClientDeletedEvent,
)
from byceps.services.whereabouts.models import (
    WhereaboutsClient,
    WhereaboutsClientAuthorityStatus,
    WhereaboutsClientID,
)

from tests.helpers import generate_token, generate_uuid


def test_register_client():
    actual_candidate, actual_event = (
        whereabouts_client_domain_service.register_client(
            button_count=3, audio_output=True
        )
    )

    assert actual_candidate.id is not None
    assert actual_candidate.registered_at is not None

    assert isinstance(actual_event, WhereaboutsClientRegisteredEvent)
    assert actual_event.occurred_at is not None
    assert actual_event.initiator is None
    assert actual_event.client_id is not None


def test_approve_client(make_client, admin_user):
    pending_client = make_client(WhereaboutsClientAuthorityStatus.pending)

    actual_client, actual_event = (
        whereabouts_client_domain_service.approve_client(
            pending_client, admin_user
        )
    )

    assert (
        actual_client.authority_status
        == WhereaboutsClientAuthorityStatus.approved
    )
    assert actual_client.token is not None

    assert isinstance(actual_event, WhereaboutsClientApprovedEvent)
    assert actual_event.occurred_at is not None
    assert actual_event.initiator == EventUser.from_user(admin_user)
    assert actual_event.client_id is not None


def test_delete_client(make_client, admin_user):
    approved_client = make_client(WhereaboutsClientAuthorityStatus.approved)

    actual_client, actual_event = (
        whereabouts_client_domain_service.delete_client(
            approved_client, admin_user
        )
    )

    assert (
        actual_client.authority_status
        == WhereaboutsClientAuthorityStatus.deleted
    )
    assert actual_client.token is None

    assert isinstance(actual_event, WhereaboutsClientDeletedEvent)
    assert actual_event.occurred_at is not None
    assert actual_event.initiator == EventUser.from_user(admin_user)
    assert actual_event.client_id is not None


@pytest.fixture(scope='module')
def make_client():
    def _wrapper(
        authority_status: WhereaboutsClientAuthorityStatus,
    ) -> WhereaboutsClient:
        registered_at = datetime.utcnow()

        return WhereaboutsClient(
            id=WhereaboutsClientID(generate_uuid()),
            registered_at=registered_at,
            button_count=3,
            audio_output=True,
            authority_status=authority_status,
            token=generate_token(),
            name=None,
            location=None,
            description=None,
            config_id=None,
            signed_on=False,
            latest_activity_at=registered_at,
        )

    return _wrapper
