"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.user import (
    event_service as user_event_service,
    service as user_service,
)


@pytest.fixture(scope='module')
def initialized_user(make_user):
    return make_user(
        'InitializedUser',
        email_address='hoarder@mailhost.example',
        email_address_verified=True,
        initialized=True,
    )


def test_invalidation_of_initialized_user(api_client, initialized_user):
    user = initialized_user

    user_before = user_service.get_db_user(user.id)
    assert user_before.email_address_verified

    response = send_request(api_client, user.email_address)
    assert response.status_code == 204

    user_after = user_service.get_db_user(user.id)
    assert not user_after.email_address_verified

    events = user_event_service.get_events_of_type_for_user(
        'user-email-address-invalidated', user.id
    )
    assert len(events) == 1
    assert events[0].data == {
        'email_address': 'hoarder@mailhost.example',
        'reason': 'unknown host',
    }


def test_invalidation_of_unknown_email_address(api_client):
    response = send_request(api_client, 'unknown_mailbox@mailhost.example')
    assert response.status_code == 404


def send_request(api_client, email_address):
    url = '/api/v1/users/invalidate_email_address'
    data = {
        'email_address': email_address,
        'reason': 'unknown host',
    }
    return api_client.post(url, json=data)
