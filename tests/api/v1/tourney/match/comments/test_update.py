"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.tourney import (
    match_comment_service as comment_service,
    match_service,
)


def test_update_comment(api_client, api_client_authz_header, comment, player):
    original_comment = comment_service.get_comment(comment.id)
    assert original_comment.body_text == 'Something stupid.'
    assert original_comment.body_html == 'Something stupid.'
    assert original_comment.last_edited_at is None
    assert original_comment.last_edited_by is None

    response = request_comment_update(
        api_client, api_client_authz_header, comment.id, player.id
    )

    assert response.status_code == 204

    updated_comment = comment_service.get_comment(comment.id)
    assert updated_comment.body_text == '[i]This[/i] is better!'
    assert updated_comment.body_html == '<em>This</em> is better!'
    assert updated_comment.last_edited_at is not None
    assert updated_comment.last_edited_by is not None
    assert updated_comment.last_edited_by.id == player.id


def test_update_nonexistant_comment(
    api_client, api_client_authz_header, player
):
    unknown_comment_id = '00000000-0000-0000-0000-000000000000'

    response = request_comment_update(
        api_client, api_client_authz_header, unknown_comment_id, player.id
    )

    assert response.status_code == 404


# helpers


@pytest.fixture
def player(user):
    return user


@pytest.fixture
def match(app):
    return match_service.create_match()


@pytest.fixture
def comment(match, player):
    body = 'Something stupid.'

    return comment_service.create_comment(match.id, player.id, body)


def request_comment_update(
    api_client, api_client_authz_header, comment_id, editor_id
):
    url = f'/api/v1/tourney/match_comments/{comment_id}'

    headers = [api_client_authz_header]
    json_data = {
        'editor_id': editor_id,
        'body': '[i]This[/i] is better!',
    }

    return api_client.patch(url, headers=headers, json=json_data)
