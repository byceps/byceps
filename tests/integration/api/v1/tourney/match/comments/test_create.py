"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.database import db
from byceps.services.tourney.dbmodels.match_comment import (
    MatchComment as DbMatchComment,
)
from byceps.services.tourney import (
    match_comment_service as comment_service,
    match_service,
)


def test_create_comment(api_client, api_client_authz_header, user, match):
    response = request_comment_creation(
        api_client, api_client_authz_header, match.id, user.id
    )

    assert response.status_code == 201
    assert get_comment_count_for_match(match.id) == 1

    comment_id = get_comment_id_from_location_header(response)
    comment = get_comment(comment_id)
    assert comment.match_id == match.id
    assert comment.created_at is not None
    assert comment.created_by.id == user.id
    assert comment.body_text == 'gg [i]lol[/i]'
    assert comment.body_html == 'gg <em>lol</em>'
    assert comment.last_edited_at is None
    assert comment.last_edited_by is None
    assert not comment.hidden
    assert comment.hidden_at is None
    assert comment.hidden_by is None


def test_create_comment_on_nonexistent_match(
    api_client, api_client_authz_header, user
):
    unknown_match_id = '00000000-0000-0000-0000-000000000000'

    response = request_comment_creation(
        api_client, api_client_authz_header, unknown_match_id, user.id
    )

    assert response.status_code == 400
    assert get_comment_count_for_match(unknown_match_id) == 0


def test_create_comment_by_suspended_user(
    api_client, api_client_authz_header, suspended_user, match
):
    response = request_comment_creation(
        api_client, api_client_authz_header, match.id, suspended_user.id
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


@pytest.fixture
def match(api_app):
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
    return db.session \
        .query(DbMatchComment) \
        .filter_by(match_id=match_id) \
        .count()
