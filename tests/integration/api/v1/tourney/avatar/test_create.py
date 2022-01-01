"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path

from byceps.services.tourney.avatar import service as avatar_service


def test_create(api_client, api_client_authz_header, party, user):
    response = send_request(
        api_client, api_client_authz_header, party.id, user.id
    )

    assert response.status_code == 201

    tear_down_avatar(response)


def test_create_fails_with_unknown_user_id(
    api_client, api_client_authz_header, party
):
    unknown_user_id = '99999999-9999-9999-9999-999999999999'

    response = send_request(
        api_client, api_client_authz_header, party.id, unknown_user_id
    )

    assert response.status_code == 400


def test_create_fails_with_uninitialized_user(
    api_client, api_client_authz_header, party, uninitialized_user,
):
    response = send_request(
        api_client, api_client_authz_header, party.id, uninitialized_user.id
    )

    assert response.status_code == 400


def test_create_fails_with_suspended_user(
    api_client, api_client_authz_header, party, suspended_user
):
    response = send_request(
        api_client, api_client_authz_header, party.id, suspended_user.id
    )

    assert response.status_code == 400


def test_create_fails_with_deleted_user(
    api_client, api_client_authz_header, party, deleted_user
):
    response = send_request(
        api_client, api_client_authz_header, party.id, deleted_user.id
    )

    assert response.status_code == 400


# helpers


def send_request(api_client, api_client_authz_header, party_id, creator_id):
    url = f'/api/v1/tourney/avatars'

    headers = [api_client_authz_header]
    with Path('tests/fixtures/images/image.png').open('rb') as image_file:
        form_data = {
            'image': image_file,
            'party_id': party_id,
            'creator_id': creator_id,
        }

        return api_client.post(url, headers=headers, data=form_data)


def tear_down_avatar(response):
    avatar_id = extract_avatar_id(response)
    avatar_service.delete_avatar_image(avatar_id)


def extract_avatar_id(response) -> str:
    filename = response.location.rsplit('/', 1)[1]
    return filename.split('.')[0]
