"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


def test_index_for_party(seating_admin_client, party):
    url = f'/admin/seating/{party.id}'
    response = seating_admin_client.get(url)
    assert response.status_code == 200


def test_area_index(seating_admin_client, party):
    url = f'/admin/seating/parties/{party.id}/areas'
    response = seating_admin_client.get(url)
    assert response.status_code == 200


def test_seat_group_index(seating_admin_client, party):
    url = f'/admin/seating/parties/{party.id}/seat_groups'
    response = seating_admin_client.get(url)
    assert response.status_code == 200
