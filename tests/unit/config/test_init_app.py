"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.config.errors import ConfigurationError
from byceps.config.integration import init_app
from byceps.config.models import AppMode


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('admin', AppMode.admin),
        ('api', AppMode.api),
        ('cli', AppMode.cli),
        ('site', AppMode.site),
        ('worker', AppMode.worker),
    ],
)
def test_init_app(make_app, value: str, expected: AppMode):
    app = make_app(AppMode.cli)

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
def test_init_app_invalid_app_mode(make_app, value: str | None):
    app = make_app(AppMode.cli)

    app.config['APP_MODE'] = value

    with pytest.raises(ConfigurationError):
        init_app(app)
