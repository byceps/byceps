"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.tourney import (
    match_comment_service as comment_service,
    match_service,
)


def test_view_for_match(
    api_client, api_client_authz_header, match, comment
):
    url = f'/api/tourney/matches/{match.id}/comments'
    headers = [api_client_authz_header]

    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.get_json() == {
        'comments': [
            {
                'comment_id': str(comment.id),
                'match_id': str(comment.match_id),
                'created_at': comment.created_at.isoformat(),
                'creator': {
                    'user_id': str(comment.creator.id),
                    'screen_name': comment.creator.screen_name,
                    'suspended': False,
                    'deleted': False,
                    'avatar_url': None,
                    'is_orga': False,
                },
                'body': 'Denn man tau.',
                'last_edited_at': None,
                'last_editor': None,
                'hidden': False,
                'hidden_at': None,
                'hidden_by_id': None,
            }
        ]
    }


def test_view_for_match_with_edited_comment(
    api_client, api_client_authz_header, match, edited_comment
):
    url = f'/api/tourney/matches/{match.id}/comments'
    headers = [api_client_authz_header]

    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.get_json() == {
        'comments': [
            {
                'comment_id': str(edited_comment.id),
                'match_id': str(edited_comment.match_id),
                'created_at': edited_comment.created_at.isoformat(),
                'creator': {
                    'user_id': str(edited_comment.creator.id),
                    'screen_name': edited_comment.creator.screen_name,
                    'suspended': False,
                    'deleted': False,
                    'avatar_url': None,
                    'is_orga': False,
                },
                'body': 'So nicht, Freundchen!',
                'last_edited_at': edited_comment.last_edited_at.isoformat(),
                'last_editor': {
                    'user_id': str(edited_comment.last_edited_by.id),
                    'screen_name': edited_comment.last_edited_by.screen_name,
                    'suspended': False,
                    'deleted': False,
                    'avatar_url': None,
                    'is_orga': False,
                },
                'hidden': False,
                'hidden_at': None,
                'hidden_by_id': None,
            }
        ]
    }


# helpers


@pytest.fixture
def match(app):
    return match_service.create_match()


@pytest.fixture
def comment(app, match, user):
    return comment_service.create_comment(match.id, user.id, 'Denn man tau.')


@pytest.fixture
def edited_comment(app, comment, admin):
    comment_service.update_comment(
        comment.id, admin.id, 'So nicht, Freundchen!'
    )
    return comment_service.get_comment(comment.id)
