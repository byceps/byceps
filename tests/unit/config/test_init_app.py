"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.byceps_app import BycepsApp
from byceps.config.errors import ConfigurationError
from byceps.config.integration import init_app
from byceps.config.models import AppMode


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('base', AppMode.base),
        ('admin', AppMode.admin),
        ('cli', AppMode.cli),
        ('site', AppMode.site),
        ('worker', AppMode.worker),
    ],
)
def test_init_app(app: BycepsApp, value: str, expected: AppMode):
    app.config['APP_MODE'] = value

    if expected == AppMode.site:
        app.config['SITE_ID'] = 'site01'

    init_app(app)

    assert app.byceps_app_mode == expected


@pytest.mark.parametrize(
    'value',
    [
        None,
        '',
        'invalid',
    ],
)
def test_init_app_invalid_app_mode(app: BycepsApp, value: str | None):
    app.config['APP_MODE'] = value

    with pytest.raises(ConfigurationError):
        init_app(app)


@pytest.fixture(scope='module')
def app(make_app) -> BycepsApp:
    return make_app()
