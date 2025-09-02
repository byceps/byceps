"""
:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator

import pytest

from byceps.services.global_setting import global_setting_service
from byceps.services.global_setting.models import GlobalSetting
from byceps.services.whereabouts import whereabouts_client_service


URL = '/v1/whereabouts/client/register'
LOCATION_PREFIX = '/v1/whereabouts/client/registration_status/'


def test_registration_closed(setting_registration_closed, api_client):
    assert not whereabouts_client_service.is_registration_open()

    payload = {
        'button_count': 3,
        'audio_output': True,
    }

    response = send_request(api_client, payload)

    assert response.status_code == 403


def test_success(setting_registration_open, api_client):
    assert whereabouts_client_service.is_registration_open()

    payload = {
        'button_count': 3,
        'audio_output': True,
    }

    response = send_request(api_client, payload)

    assert response.status_code == 201
    assert response.location.startswith(LOCATION_PREFIX)

    client_id = response.location.removeprefix(LOCATION_PREFIX)
    client = whereabouts_client_service.find_client(client_id)
    assert response.json == {
        'client_id': client_id,
        'token': client.token,
    }


def send_request(api_client, payload: dict[str, bool | int | str]):
    return api_client.post(URL, json=payload)


@pytest.fixture()
def setting_registration_open(api_app) -> Iterator[GlobalSetting]:
    setting = global_setting_service.create_setting(
        'whereabouts_client_registration_status', 'open'
    )

    yield setting

    global_setting_service.remove_setting(setting.name)


@pytest.fixture()
def setting_registration_closed(api_app) -> Iterator[GlobalSetting]:
    setting = global_setting_service.create_setting(
        'whereabouts_client_registration_status', 'closed'
    )

    yield setting

    global_setting_service.remove_setting(setting.name)
