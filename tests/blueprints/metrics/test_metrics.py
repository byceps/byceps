"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

def test_metrics(make_admin_app):
    client = _get_test_client(make_admin_app, True)

    response = client.get('/metrics')

    assert response.status_code == 200
    assert response.content_type == 'text/plain; version=0.0.4; charset=utf-8'
    assert response.mimetype == 'text/plain'
    assert response.get_data(as_text=True) == (
        'users_enabled_count 0\n'
        'users_disabled_count 0\n'
        'users_suspended_count 0\n'
        'users_deleted_count 0\n'
        'users_total_count 0\n'
    )


def test_disabled_metrics(make_admin_app):
    client = _get_test_client(make_admin_app, False)

    response = client.get('/metrics')

    assert response.status_code == 404


def _get_test_client(make_admin_app, metrics_enabled):
    config_overrides = {'METRICS_ENABLED': metrics_enabled}
    app = make_admin_app(**config_overrides)

    return app.test_client()
