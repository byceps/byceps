"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.tourney.models.match_comment import (
    MatchComment as DbMatchComment,
)
from byceps.services.tourney import (
    match_comment_service as comment_service,
    match_service,
)
from byceps.services.user import command_service as user_command_service

from tests.helpers import create_user


def test_create_comment(api_client, api_client_authz_header, player, match):
    response = request_comment_creation(
        api_client, api_client_authz_header, match.id, player.id
    )

    assert response.status_code == 201
    assert get_comment_count_for_match(match.id) == 1

    comment_id = get_comment_id_from_location_header(response)
    comment = get_comment(comment_id)
    assert comment.match_id == match.id
    assert comment.created_at is not None
    assert comment.created_by.id == player.id
    assert comment.body_text == 'gg [i]lol[/i]'
    assert comment.body_html == 'gg <em>lol</em>'
    assert comment.last_edited_at is None
    assert comment.last_edited_by is None
    assert not comment.hidden
    assert comment.hidden_at is None
    assert comment.hidden_by is None


def test_create_comment_on_nonexistent_match(
    api_client, api_client_authz_header, player
):
    unknown_match_id = '00000000-0000-0000-0000-000000000000'

    response = request_comment_creation(
        api_client, api_client_authz_header, unknown_match_id, player.id
    )

    assert response.status_code == 400
    assert get_comment_count_for_match(unknown_match_id) == 0


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
    url = f'/api/v1/tourney/match_comments'

    headers = [api_client_authz_header]
    json_data = {
        'match_id': str(match_id),
        'creator_id': creator_id,
        'body': 'gg [i]lol[/i]',
    }

    return api_client.post(url, headers=headers, json=json_data)


def get_comment_id_from_location_header(response):
    location_header = response.headers['Location']
    return location_header.rpartition('/')[-1]


def get_comment(comment_id):
    return comment_service.get_comment(comment_id)


def get_comment_count_for_match(match_id):
    return DbMatchComment.query.for_match(match_id).count()
