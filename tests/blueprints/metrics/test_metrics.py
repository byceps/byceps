"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from ...conftest import database_recreated


# To be overridden by test parametrization
@pytest.fixture
def config_overrides():
    return {}


@pytest.fixture
def client(config_overrides, make_admin_app, db):
    app = make_admin_app(**config_overrides)
    with app.app_context():
        with database_recreated(db):
            yield app.test_client()


@pytest.mark.parametrize('config_overrides', [{'METRICS_ENABLED': True}])
def test_metrics(client):
    response = client.get('/metrics')

    assert response.status_code == 200
    assert response.content_type == 'text/plain; version=0.0.4; charset=utf-8'
    assert response.mimetype == 'text/plain'
    assert response.get_data(as_text=True) == (
        'users_active_count 0\n'
        'users_uninitialized_count 0\n'
        'users_suspended_count 0\n'
        'users_deleted_count 0\n'
        'users_total_count 0\n'
    )


@pytest.mark.parametrize('config_overrides', [{'METRICS_ENABLED': False}])
def test_disabled_metrics(client):
    response = client.get('/metrics')

    assert response.status_code == 404
