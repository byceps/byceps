"""
:Copyright: 2022-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from freezegun import freeze_time
import pytest

from byceps.services.party.models import Party
from byceps.services.user.models.user import User
from byceps.services.whereabouts import (
    whereabouts_client_service,
    whereabouts_service,
)
from byceps.services.whereabouts.models import Whereabouts

from tests.helpers import generate_token


URL = '/v1/whereabouts/statuses'


def test_success(
    api_client,
    client_token_header,
    whereabouts_client,
    user: User,
    party: Party,
    whereabouts: Whereabouts,
):
    status_before = whereabouts_service.find_status(user, party)
    assert status_before is None

    now = datetime(2025, 11, 24, 20, 44, 35)

    payload = {
        'user_id': str(user.id),
        'party_id': str(party.id),
        'whereabouts_name': str(whereabouts.name),
    }

    with freeze_time(now):
        response = send_request(api_client, client_token_header, payload)

    assert response.status_code == 204

    status_after = whereabouts_service.find_status(user, party)
    assert status_after is not None
    assert status_after.user.id == user.id
    assert status_after.user.screen_name == user.screen_name
    assert status_after.user.avatar_url == user.avatar_url
    assert status_after.whereabouts_id == whereabouts.id
    assert status_after.set_at == now


def test_unauthorized(api_client):
    response = api_client.post(URL)

    assert response.status_code == 401
    assert response.json is None


def test_empty_payload(api_client, client_token_header):
    payload: dict[str, str] = {}

    response = send_request(api_client, client_token_header, payload)

    assert response.status_code == 400


def test_unknown_user_id(
    api_client,
    client_token_header,
    whereabouts_client,
    party: Party,
    whereabouts: Whereabouts,
):
    unknown_user_id = '00000000000000000000000000000000'

    payload = {
        'user_id': unknown_user_id,
        'party_id': str(party.id),
        'whereabouts_name': str(whereabouts.name),
    }

    response = send_request(api_client, client_token_header, payload)

    assert response.status_code == 400


def test_unknown_party_id(
    api_client,
    client_token_header,
    whereabouts_client,
    user: User,
    whereabouts: Whereabouts,
):
    payload = {
        'user_id': str(user.id),
        'party_id': 'unknown-party-id',
        'whereabouts_name': str(whereabouts.name),
    }

    response = send_request(api_client, client_token_header, payload)

    assert response.status_code == 400


def test_unknown_whereabouts_name(
    api_client,
    client_token_header,
    whereabouts_client,
    user: User,
    party: Party,
    whereabouts: Whereabouts,
):
    payload = {
        'user_id': str(user.id),
        'party_id': str(party.id),
        'whereabouts_name': 'unknown-whereabouts-name',
    }

    response = send_request(api_client, client_token_header, payload)

    assert response.status_code == 400


@pytest.fixture(scope='module')
def whereabouts_client(admin_user: User):
    client, _ = whereabouts_client_service.register_client(
        button_count=3, audio_output=False
    )
    approved_client, _ = whereabouts_client_service.approve_client(
        client, admin_user
    )
    return approved_client


@pytest.fixture(scope='module')
def user(make_user) -> User:
    return make_user()


@pytest.fixture(scope='module')
def whereabouts(party) -> Whereabouts:
    name = description = generate_token()
    return whereabouts_service.create_whereabouts(party, name, description)


@pytest.fixture(scope='module')
def client_token_header(whereabouts_client):
    return 'Authorization', f'Bearer {whereabouts_client.token}'


def send_request(api_client, client_token_header, payload: dict[str, str]):
    headers = [client_token_header]
    return api_client.post(URL, headers=headers, json=payload)
