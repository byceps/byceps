"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from base64 import b64encode

import pytest

from byceps.services.tourney.models.match import MatchComment
from byceps.services.tourney import match_service
from byceps.services.user import command_service as user_command_service

from tests.api.helpers import assemble_authorization_header
from tests.conftest import database_recreated
from tests.helpers import (
    create_email_config,
    create_site,
    create_user,
    http_client,
)


def test_create_comment(app, site, player, match):
    response = request_comment_creation(app, match.id, player.id)

    assert response.status_code == 201
    assert get_comment_count_for_match(match.id) == 1


def test_create_comment_on_nonexistent_match(app, site, player):
    unknown_match_id = '00000000-0000-0000-0000-000000000000'

    response = request_comment_creation(app, unknown_match_id, player.id)

    assert response.status_code == 404


def test_create_comment_by_suspended_user(app, site, cheater, match):
    response = request_comment_creation(app, match.id, cheater.id)

    assert response.status_code == 400
    assert get_comment_count_for_match(match.id) == 0


def test_create_comment_by_unknown_user(app, site, match):
    unknown_user_id = '00000000-0000-0000-0000-000000000000'

    response = request_comment_creation(app, match.id, unknown_user_id)

    assert response.status_code == 400
    assert get_comment_count_for_match(match.id) == 0


# helpers


@pytest.fixture(scope='module')
def app(db, party_app):
    with party_app.app_context():
        with database_recreated(db):
            yield party_app


@pytest.fixture(scope='module')
def site():
    create_email_config()
    create_site()


@pytest.fixture(scope='module')
def player(app):
    return create_user()


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


def request_comment_creation(app, match_id, creator_id):
    url = f'/api/tourney/matches/{match_id}/comments'

    headers = [assemble_authorization_header('just-say-PLEASE')]

    form_data = {'creator_id': creator_id, 'body': 'gg'}

    with http_client(app) as client:
        return client.post(url, headers=headers, data=form_data)


def get_comment_count_for_match(match_id):
    return MatchComment.query.for_match(match_id).count()
