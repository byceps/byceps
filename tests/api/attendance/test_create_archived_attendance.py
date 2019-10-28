"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.ticketing import attendance_service

from tests.api.helpers import assemble_authorization_header
from tests.helpers import create_brand, create_party


def test_create_archived_attendance(admin_app_with_db, party, normal_user):
    user = normal_user

    before = attendance_service.get_attended_parties(user.id)
    assert before == []

    url = f'/api/attendances/archived_attendances'
    headers = [assemble_authorization_header('just-say-PLEASE')]
    form_data = {
        'user_id': str(user.id),
        'party_id': str(party.id),
    }

    with admin_app_with_db.test_client() as client:
        response = client.post(url, headers=headers, data=form_data)
    assert response.status_code == 204

    actual = attendance_service.get_attended_parties(user.id)
    actual_ids = [party.id for party in actual]
    assert actual_ids == [party.id]


@pytest.fixture
def party():
    brand = create_brand()
    return create_party(brand.id)
