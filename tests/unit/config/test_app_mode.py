"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.config.models import AppMode


def test_is_admin():
    app_mode = AppMode.admin

    assert app_mode.is_admin()
    assert not app_mode.is_api()
    assert not app_mode.is_cli()
    assert not app_mode.is_site()
    assert not app_mode.is_worker()


def test_is_api():
    app_mode = AppMode.api

    assert not app_mode.is_admin()
    assert app_mode.is_api()
    assert not app_mode.is_cli()
    assert not app_mode.is_site()
    assert not app_mode.is_worker()


def test_is_cli():
    app_mode = AppMode.cli

    assert not app_mode.is_admin()
    assert not app_mode.is_api()
    assert app_mode.is_cli()
    assert not app_mode.is_site()
    assert not app_mode.is_worker()


def test_is_site():
    app_mode = AppMode.site

    assert not app_mode.is_admin()
    assert not app_mode.is_api()
    assert not app_mode.is_cli()
    assert app_mode.is_site()
    assert not app_mode.is_worker()


def test_is_worker():
    app_mode = AppMode.worker

    assert not app_mode.is_admin()
    assert not app_mode.is_api()
    assert not app_mode.is_cli()
    assert not app_mode.is_site()
    assert app_mode.is_worker()
