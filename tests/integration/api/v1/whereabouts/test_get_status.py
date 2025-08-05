"""
:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.party.models import Party
from byceps.services.user.models.user import User
from byceps.services.whereabouts import (
    whereabouts_client_service,
    whereabouts_service,
)
from byceps.services.whereabouts.models import Whereabouts, WhereaboutsStatus

from tests.helpers import generate_token


CONTENT_TYPE_JSON = 'application/json'


def test_get_status(
    api_client,
    client_token_header,
    user: User,
    party: Party,
    whereabouts: Whereabouts,
    status: WhereaboutsStatus,
):
    response = send_request(api_client, client_token_header, user, party)

    assert response.status_code == 200
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON

    response_data = response.json
    assert response_data['user']['id'] == str(user.id)
    assert response_data['user']['screen_name'] == user.screen_name
    assert response_data['user']['avatar_url'] == user.avatar_url
    assert response_data['whereabouts']['id'] == str(whereabouts.id)
    assert response_data['whereabouts']['name'] == whereabouts.name
    assert (
        response_data['whereabouts']['description'] == whereabouts.description
    )
    assert response_data['set_at'] == status.set_at.isoformat()


def test_unauthorized(api_client, user: User, party: Party):
    url = build_url(user, party)
    response = api_client.get(url)

    assert response.status_code == 401
    assert response.json is None


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
def whereabouts(party: Party) -> Whereabouts:
    name = description = generate_token()
    return whereabouts_service.create_whereabouts(party, name, description)


@pytest.fixture(scope='module')
def client_token_header(whereabouts_client):
    return 'Authorization', f'Bearer {whereabouts_client.token}'


@pytest.fixture(scope='module')
def status(
    whereabouts_client, user: User, whereabouts: Whereabouts
) -> WhereaboutsStatus:
    status, _, _ = whereabouts_service.set_status(
        whereabouts_client, user, whereabouts
    )
    return status


def send_request(api_client, client_token_header, user: User, party: Party):
    url = build_url(user, party)
    return api_client.get(url, headers=[client_token_header])


def build_url(user: User, party: Party) -> str:
    return f'/v1/whereabouts/statuses/{user.id}/{party.id}'
