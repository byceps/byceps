"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.tourney.models.match import MatchComment
from byceps.services.tourney import match_service
from byceps.services.user import command_service as user_command_service

from tests.helpers import create_user


def test_create_comment(api_client, api_client_authz_header, player, match):
    response = request_comment_creation(
        api_client, api_client_authz_header, match.id, player.id
    )

    assert response.status_code == 201
    assert get_comment_count_for_match(match.id) == 1


def test_create_comment_on_nonexistent_match(
    api_client, api_client_authz_header, player
):
    unknown_match_id = '00000000-0000-0000-0000-000000000000'

    response = request_comment_creation(
        api_client, api_client_authz_header, unknown_match_id, player.id
    )

    assert response.status_code == 404


def test_create_comment_by_suspended_user(
    api_client, api_client_authz_header, cheater, match
):
    response = request_comment_creation(
        api_client, api_client_authz_header, match.id, cheater.id
    )

    assert response.status_code == 400
    assert get_comment_count_for_match(match.id) == 0


def test_create_comment_by_unknown_user(
    api_client, api_client_authz_header, match
):
    unknown_user_id = '00000000-0000-0000-0000-000000000000'

    response = request_comment_creation(
        api_client, api_client_authz_header, match.id, unknown_user_id
    )

    assert response.status_code == 400
    assert get_comment_count_for_match(match.id) == 0


# helpers


@pytest.fixture(scope='module')
def player(user):
    return user


@pytest.fixture(scope='module')
def cheater(app):
    user = create_user('Cheater!')

    user_command_service.suspend_account(
        user.id, user.id, reason='I cheat, therefore I lame.'
    )

    return user


@pytest.fixture
def match(app):
    return match_service.create_match()


def request_comment_creation(
    api_client, api_client_authz_header, match_id, creator_id
):
    url = f'/api/tourney/matches/{match_id}/comments'

    headers = [api_client_authz_header]
    json_data = {'creator_id': creator_id, 'body': 'gg'}

    return api_client.post(url, headers=headers, json=json_data)


def get_comment_count_for_match(match_id):
    return MatchComment.query.for_match(match_id).count()
