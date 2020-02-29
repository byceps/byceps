"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


def test_create(
    data_path, app, api_client, api_client_authz_header, party, user
):
    app.config['PATH_DATA'] = data_path

    response = send_request(
        api_client, api_client_authz_header, party.id, user.id
    )

    assert response.status_code == 201


def test_create_fails_with_unknown_user_id(
    data_path, app, api_client, api_client_authz_header, party
):
    app.config['PATH_DATA'] = data_path

    unknown_user_id = '99999999-9999-9999-9999-999999999999'

    response = send_request(
        api_client, api_client_authz_header, party.id, unknown_user_id
    )

    assert response.status_code == 400


def test_create_fails_with_uninitialized_user(
    data_path,
    app,
    api_client,
    api_client_authz_header,
    party,
    uninitialized_user,
):
    app.config['PATH_DATA'] = data_path

    response = send_request(
        api_client, api_client_authz_header, party.id, uninitialized_user.id
    )

    assert response.status_code == 400


def test_create_fails_with_suspended_user(
    data_path, app, api_client, api_client_authz_header, party, suspended_user
):
    app.config['PATH_DATA'] = data_path

    response = send_request(
        api_client, api_client_authz_header, party.id, suspended_user.id
    )

    assert response.status_code == 400


def test_create_fails_with_deleted_user(
    data_path, app, api_client, api_client_authz_header, party, deleted_user
):
    app.config['PATH_DATA'] = data_path

    response = send_request(
        api_client, api_client_authz_header, party.id, deleted_user.id
    )

    assert response.status_code == 400


@pytest.fixture
def data_path():
    with TemporaryDirectory() as d:
        yield Path(d)


def send_request(api_client, api_client_authz_header, party_id, creator_id):
    url = f'/api/tourney/avatars'

    headers = [api_client_authz_header]
    with Path('testfixtures/images/image.png').open('rb') as image_file:
        form_data = {
            'image': image_file,
            'party_id': party_id,
            'creator_id': creator_id,
        }

        return api_client.post(url, headers=headers, data=form_data)
