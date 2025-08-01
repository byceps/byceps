"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.tourney import (
    tourney_match_comment_service,
    tourney_match_service,
)


def test_get_comment(api_client, api_client_authz_header, comment):
    url = f'http://api.acmecon.test/v1/tourney/match_comments/{comment.id}'
    headers = [api_client_authz_header]

    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.get_json() == {
        'comment_id': str(comment.id),
        'match_id': str(comment.match_id),
        'created_at': comment.created_at.isoformat(),
        'creator': {
            'user_id': str(comment.created_by.id),
            'screen_name': comment.created_by.screen_name,
            'suspended': False,
            'deleted': False,
            'avatar_url': '/static/user_avatar_fallback.svg',
            'is_orga': False,
        },
        'body_text': 'Denn man tau.',
        'body_html': 'Denn man tau.',
        'last_edited_at': None,
        'last_editor': None,
        'hidden': False,
        'hidden_at': None,
        'hidden_by': None,
    }


def test_get_comment_with_party_id(
    api_client, api_client_authz_header, comment, party
):
    url = f'http://api.acmecon.test/v1/tourney/match_comments/{comment.id}?party_id={party.id}'
    headers = [api_client_authz_header]

    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.get_json() == {
        'comment_id': str(comment.id),
        'match_id': str(comment.match_id),
        'created_at': comment.created_at.isoformat(),
        'creator': {
            'user_id': str(comment.created_by.id),
            'screen_name': comment.created_by.screen_name,
            'suspended': False,
            'deleted': False,
            'avatar_url': '/static/user_avatar_fallback.svg',
            'is_orga': False,
        },
        'body_text': 'Denn man tau.',
        'body_html': 'Denn man tau.',
        'last_edited_at': None,
        'last_editor': None,
        'hidden': False,
        'hidden_at': None,
        'hidden_by': None,
    }


def test_get_comment_with_edited_comment(
    api_client, api_client_authz_header, edited_comment
):
    comment = edited_comment

    url = f'http://api.acmecon.test/v1/tourney/match_comments/{comment.id}'
    headers = [api_client_authz_header]

    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.get_json() == {
        'comment_id': str(comment.id),
        'match_id': str(comment.match_id),
        'created_at': comment.created_at.isoformat(),
        'creator': {
            'user_id': str(comment.created_by.id),
            'screen_name': comment.created_by.screen_name,
            'suspended': False,
            'deleted': False,
            'avatar_url': '/static/user_avatar_fallback.svg',
            'is_orga': False,
        },
        'body_text': '[b]So nicht[/b], Freundchen!',
        'body_html': '<strong>So nicht</strong>, Freundchen!',
        'last_edited_at': comment.last_edited_at.isoformat(),
        'last_editor': {
            'user_id': str(comment.last_edited_by.id),
            'screen_name': comment.last_edited_by.screen_name,
            'suspended': False,
            'deleted': False,
            'avatar_url': '/static/user_avatar_fallback.svg',
            'is_orga': False,
        },
        'hidden': False,
        'hidden_at': None,
        'hidden_by': None,
    }


# helpers


@pytest.fixture()
def match(database):
    return tourney_match_service.create_match()


@pytest.fixture()
def comment(database, match, user):
    return tourney_match_comment_service.create_comment(
        match.id, user, 'Denn man tau.'
    )


@pytest.fixture()
def edited_comment(database, comment, admin_user):
    tourney_match_comment_service.update_comment(
        comment.id, admin_user, '[b]So nicht[/b], Freundchen!'
    )
    return tourney_match_comment_service.get_comment(comment.id)
