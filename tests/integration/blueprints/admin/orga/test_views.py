"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.orga import service as orga_service


def test_persons_for_brand(orga_admin_client, brand):
    url = f'/admin/orgas/persons/{brand.id}'
    response = orga_admin_client.get(url)
    assert response.status_code == 200


def test_create_orgaflag_form(orga_admin_client, brand):
    url = f'/admin/orgas/persons/{brand.id}/create'
    response = orga_admin_client.get(url)
    assert response.status_code == 200


def test_create_and_remove_orgaflag(orga_admin_client, brand, make_user):
    user = make_user('OrgaCandidate')
    assert not orga_service.is_user_orga(user.id)

    url = f'/admin/orgas/persons/{brand.id}'
    form_data = {
        'user': user.screen_name,
    }
    response = orga_admin_client.post(url, data=form_data)
    assert response.status_code == 302
    assert orga_service.is_user_orga(user.id)

    url = f'/admin/orgas/persons/{brand.id}/{user.id}'
    response = orga_admin_client.delete(url)
    assert response.status_code == 204
    assert not orga_service.is_user_orga(user.id)


def test_export_persons(orga_admin_client, brand):
    url = f'/admin/orgas/persons/{brand.id}/export'
    response = orga_admin_client.get(url)
    assert response.status_code == 200


def test_birthdays(orga_admin_client, brand):
    url = f'/admin/orgas/birthdays'
    response = orga_admin_client.get(url)
    assert response.status_code == 200
