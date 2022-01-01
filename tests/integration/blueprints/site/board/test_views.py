"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import log_in_user

from .helpers import find_topic


@pytest.fixture(scope='package')
def board_user(make_user):
    user = make_user()
    log_in_user(user.id)
    yield user


@pytest.fixture(scope='module')
def anonymous_client(make_client, site_app):
    return make_client(site_app)


@pytest.fixture(scope='module')
def logged_in_client(make_client, site_app, board_user):
    return make_client(site_app, user_id=board_user.id)


def test_category_index_anonymously(site_app, anonymous_client):
    url = '/board/'
    assert_success_response(anonymous_client, url)


def test_category_index_logged_in(site_app, logged_in_client):
    url = '/board/'
    assert_success_response(logged_in_client, url)


def test_category_view_anonymously(site_app, anonymous_client, category):
    url = f'/board/categories/{category.slug}'
    assert_success_response(anonymous_client, url)


def test_category_view_logged_in(site_app, logged_in_client, category):
    url = f'/board/categories/{category.slug}'
    assert_success_response(logged_in_client, url)


def test_topic_index_anonymously(site_app, anonymous_client, topic):
    url = '/board/topics'
    assert_success_response(anonymous_client, url)


def test_topic_index_logged_in(site_app, logged_in_client, topic):
    url = '/board/topics'
    assert_success_response(logged_in_client, url)


def test_topic_view_anonymously(site_app, anonymous_client, topic):
    url = f'/board/topics/{topic.id}'
    assert_success_response(anonymous_client, url)


def test_topic_view_logged_in(site_app, logged_in_client, topic):
    url = f'/board/topics/{topic.id}'
    assert_success_response(logged_in_client, url)


# helpers


def assert_success_response(client, url):
    response = client.get(url)
    assert response.status_code == 200
