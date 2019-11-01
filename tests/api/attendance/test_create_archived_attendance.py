"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.ticketing import attendance_service


def test_create_archived_attendance(
    api_client, api_client_authz_header, party, user
):
    before = attendance_service.get_attended_parties(user.id)
    assert before == []

    url = f'/api/attendances/archived_attendances'
    headers = [api_client_authz_header]
    form_data = {
        'user_id': str(user.id),
        'party_id': str(party.id),
    }

    response = api_client.post(url, headers=headers, data=form_data)
    assert response.status_code == 204

    actual = attendance_service.get_attended_parties(user.id)
    actual_ids = [party.id for party in actual]
    assert actual_ids == [party.id]
