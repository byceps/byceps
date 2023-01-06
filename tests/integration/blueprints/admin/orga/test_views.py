"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.orga import orga_service


def test_persons_for_brand(orga_admin_client, brand):
    url = f'/admin/orgas/persons/{brand.id}'
    response = orga_admin_client.get(url)
    assert response.status_code == 200


def test_create_orgaflag_form(orga_admin_client, brand):
    url = f'/admin/orgas/persons/{brand.id}/create'
    response = orga_admin_client.get(url)
    assert response.status_code == 200


def test_create_and_remove_orgaflag(orga_admin_client, brand, make_user):
    user = make_user()
    assert not is_orga_for_brand(user.id, brand.id)

    url = f'/admin/orgas/persons/{brand.id}'
    form_data = {
        'user': user.screen_name,
    }
    response = orga_admin_client.post(url, data=form_data)
    assert response.status_code == 302
    assert is_orga_for_brand(user.id, brand.id)

    url = f'/admin/orgas/persons/{brand.id}/{user.id}'
    response = orga_admin_client.delete(url)
    assert response.status_code == 204
    assert not is_orga_for_brand(user.id, brand.id)


def test_export_persons(orga_admin_client, brand):
    url = f'/admin/orgas/persons/{brand.id}/export'
    response = orga_admin_client.get(url)
    assert response.status_code == 200


def test_birthdays(orga_admin_client, brand):
    url = '/admin/orgas/birthdays'
    response = orga_admin_client.get(url)
    assert response.status_code == 200


def is_orga_for_brand(user_id, brand_id) -> bool:
    return orga_service.find_orga_flag(brand_id, user_id) is not None
