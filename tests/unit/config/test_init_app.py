"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.config.integration import init_app
from byceps.config.models import AppMode


@pytest.mark.parametrize(
    ('app_mode'),
    [
        (AppMode.admin),
        (AppMode.api),
        (AppMode.cli),
        (AppMode.site),
        (AppMode.worker),
    ],
)
def test_init_app(make_app, app_mode: AppMode):
    app = make_app(app_mode)

    if app_mode == AppMode.site:
        app.config['SITE_ID'] = 'site01'

    init_app(app)

    assert app.byceps_app_mode == app_mode
