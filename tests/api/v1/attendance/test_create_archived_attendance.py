"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.ticketing import attendance_service


@pytest.fixture
def another_user(make_user):
    yield from make_user('AnotherUser')


def test_create_archived_attendance(
    api_client, api_client_authz_header, party, user
):
    before = attendance_service.get_attended_parties(user.id)
    assert before == []

    response = send_request(
        api_client, api_client_authz_header, user.id, party.id
    )
    assert response.status_code == 204

    assert_attended_party_ids(user.id, [party.id])

    # Clean up.
    attendance_service.delete_archived_attendance(user.id, party.id)


def test_create_archived_attendance_idempotency(
    api_client, api_client_authz_header, party, another_user
):
    user = another_user

    before = attendance_service.get_attended_parties(user.id)
    assert before == []

    # First addition. Should add the party.
    response = send_request(
        api_client, api_client_authz_header, user.id, party.id
    )
    assert response.status_code == 204
    assert_attended_party_ids(user.id, [party.id])

    # Second addition for same user and party. Should be ignored.
    response = send_request(
        api_client, api_client_authz_header, user.id, party.id
    )
    assert response.status_code == 204
    assert_attended_party_ids(user.id, [party.id])

    # Clean up.
    attendance_service.delete_archived_attendance(user.id, party.id)


# helpers


def send_request(api_client, api_client_authz_header, user_id, party_id):
    url = f'/api/v1/attendances/archived_attendances'
    headers = [api_client_authz_header]
    json_data = {
        'user_id': str(user_id),
        'party_id': str(party_id),
    }

    return api_client.post(url, headers=headers, json=json_data)


def assert_attended_party_ids(user_id, expected):
    parties = attendance_service.get_attended_parties(user_id)
    actual = [party.id for party in parties]
    assert actual == expected
