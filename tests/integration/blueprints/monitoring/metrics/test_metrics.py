"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import re

import pytest


SERVER_NAME = 'admin-for-metrics.acmecon.test'
URL = f'http://{SERVER_NAME}/metrics/'


# To be overridden by test parametrization
@pytest.fixture()
def metrics_enabled():
    return False


@pytest.fixture()
def client(metrics_enabled, make_admin_app):
    app = make_admin_app(SERVER_NAME, metrics_enabled=metrics_enabled)
    with app.app_context():
        yield app.test_client()


@pytest.mark.parametrize('metrics_enabled', [True])
def test_metrics(client):
    response = client.get(URL)

    assert response.status_code == 200
    assert response.content_type == 'text/plain; version=0.0.4; charset=utf-8'
    assert response.mimetype == 'text/plain'

    # Not a full match as there can be other metrics, too.
    regex = re.compile(
        'users_active_count \\d+\n'
        'users_uninitialized_count \\d+\n'
        'users_suspended_count \\d+\n'
        'users_deleted_count \\d+\n'
        'users_total_count \\d+\n'
    )
    assert regex.search(response.get_data(as_text=True)) is not None


@pytest.mark.parametrize('metrics_enabled', [False])
def test_disabled_metrics(client):
    response = client.get(URL)

    assert response.status_code == 404
