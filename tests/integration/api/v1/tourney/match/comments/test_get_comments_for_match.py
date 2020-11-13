"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.tourney import (
    match_comment_service as comment_service,
    match_service,
)


def test_get_comments_for_match(
    api_client, api_client_authz_header, match, comment
):
    url = f'/api/v1/tourney/matches/{match.id}/comments'
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
                    'user_id': str(comment.created_by.id),
                    'screen_name': comment.created_by.screen_name,
                    'suspended': False,
                    'deleted': False,
                    'avatar_url': None,
                    'is_orga': False,
                },
                'body_text': 'Denn man tau.',
                'body_html': 'Denn man tau.',
                'last_edited_at': None,
                'last_editor': None,
                'hidden': False,
                'hidden_at': None,
                'hidden_by_id': None,
            }
        ]
    }


def test_get_comments_for_match_with_edited_comment(
    api_client, api_client_authz_header, match, edited_comment
):
    url = f'/api/v1/tourney/matches/{match.id}/comments'
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
                    'user_id': str(edited_comment.created_by.id),
                    'screen_name': edited_comment.created_by.screen_name,
                    'suspended': False,
                    'deleted': False,
                    'avatar_url': None,
                    'is_orga': False,
                },
                'body_text': '[b]So nicht[/b], Freundchen!',
                'body_html': '<strong>So nicht</strong>, Freundchen!',
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
def match(api_app):
    return match_service.create_match()


@pytest.fixture
def comment(api_app, match, user):
    return comment_service.create_comment(match.id, user.id, 'Denn man tau.')


@pytest.fixture
def edited_comment(api_app, comment, admin_user):
    comment_service.update_comment(
        comment.id, admin_user.id, '[b]So nicht[/b], Freundchen!'
    )
    return comment_service.get_comment(comment.id)
