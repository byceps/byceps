"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.orga import orga_service


BASE_URL = 'http://admin.acmecon.test'


def test_persons_for_brand(orga_admin_client, brand):
    url = f'{BASE_URL}/orgas/persons/{brand.id}'
    response = orga_admin_client.get(url)
    assert response.status_code == 200


def test_grant_orga_status_form(orga_admin_client, brand):
    url = f'{BASE_URL}/orgas/persons/{brand.id}/create'
    response = orga_admin_client.get(url)
    assert response.status_code == 200


def test_grant_and_revoke_orga_status(orga_admin_client, brand, make_user):
    user = make_user()
    assert not has_orga_status(user.id, brand.id)

    url = f'{BASE_URL}/orgas/persons/{brand.id}'
    form_data = {
        'user': user.screen_name,
    }
    response = orga_admin_client.post(url, data=form_data)
    assert response.status_code == 302
    assert has_orga_status(user.id, brand.id)

    url = f'{BASE_URL}/orgas/persons/{brand.id}/{user.id}'
    response = orga_admin_client.delete(url)
    assert response.status_code == 204
    assert not has_orga_status(user.id, brand.id)


def test_export_persons(orga_admin_client, brand):
    url = f'{BASE_URL}/orgas/persons/{brand.id}/export'
    response = orga_admin_client.get(url)
    assert response.status_code == 200


def test_birthdays(orga_admin_client, brand):
    url = f'{BASE_URL}/orgas/birthdays'
    response = orga_admin_client.get(url)
    assert response.status_code == 200


def has_orga_status(user_id, brand_id) -> bool:
    return orga_service.has_orga_status(user_id, brand_id)
