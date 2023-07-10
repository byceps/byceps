"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import pytest

from byceps.config import AppMode, ConfigurationError, init_app


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        (None, AppMode.base),
        ('base', AppMode.base),
        ('admin', AppMode.admin),
        ('cli', AppMode.cli),
        ('site', AppMode.site),
        ('worker', AppMode.worker),
    ],
)
def test_init_app(app: Flask, value: str, expected: AppMode):
    if value is not None:
        app.config['APP_MODE'] = value

    if expected == AppMode.site:
        app.config['SITE_ID'] = 'site01'

    init_app(app)

    assert app.byceps_app_mode == expected


@pytest.mark.parametrize(
    'value',
    [
        '',
        'invalid',
    ],
)
def test_init_app_error(app: Flask, value: str):
    app.config['APP_MODE'] = value

    with pytest.raises(ConfigurationError):
        init_app(app)


@pytest.fixture(scope='module')
def app() -> Flask:
    return Flask(__name__)
