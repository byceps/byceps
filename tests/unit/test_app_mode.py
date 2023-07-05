"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.config import AppMode


def test_is_admin():
    app_mode = AppMode.admin

    assert app_mode.is_admin()
    assert not app_mode.is_base()
    assert not app_mode.is_site()
    assert not app_mode.is_worker()


def test_is_base():
    app_mode = AppMode.base

    assert not app_mode.is_admin()
    assert app_mode.is_base()
    assert not app_mode.is_site()
    assert not app_mode.is_worker()


def test_is_site():
    app_mode = AppMode.site

    assert not app_mode.is_admin()
    assert not app_mode.is_base()
    assert app_mode.is_site()
    assert not app_mode.is_worker()


def test_is_worker():
    app_mode = AppMode.worker

    assert not app_mode.is_admin()
    assert not app_mode.is_base()
    assert not app_mode.is_site()
    assert app_mode.is_worker()
