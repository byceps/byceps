"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.user import (
    event_service as user_event_service,
    service as user_service,
)


def test_invalidation_of_initialized_user(
    api_client, api_client_authz_header, make_user
):
    email_address = 'hoarder@mailhost.example'

    user = make_user(
        email_address=email_address,
        email_address_verified=True,
        initialized=True,
    )

    user_before = user_service.get_db_user(user.id)
    assert user_before.email_address_verified

    response = send_request(api_client, api_client_authz_header, email_address)
    assert response.status_code == 204

    user_after = user_service.get_db_user(user.id)
    assert not user_after.email_address_verified

    events = user_event_service.get_events_of_type_for_user(
        user.id, 'user-email-address-invalidated'
    )
    assert len(events) == 1
    assert events[0].data == {
        'email_address': email_address,
        'reason': 'unknown host',
    }


def test_invalidation_of_unknown_email_address(
    api_client, api_client_authz_header
):
    response = send_request(
        api_client, api_client_authz_header, 'unknown_mailbox@mailhost.example'
    )
    assert response.status_code == 404


def send_request(api_client, api_client_authz_header, email_address):
    url = '/api/v1/users/invalidate_email_address'
    headers = [api_client_authz_header]
    data = {
        'email_address': email_address,
        'reason': 'unknown host',
    }
    return api_client.post(url, headers=headers, json=data)
