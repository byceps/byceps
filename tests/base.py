"""
tests.base
~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from byceps.application import create_app


_CONFIG_PATH = Path('../config')
CONFIG_FILENAME_TEST_SITE = _CONFIG_PATH / 'test_site.py'
CONFIG_FILENAME_TEST_ADMIN = _CONFIG_PATH / 'test_admin.py'


def create_admin_app(config_overrides: Optional[Dict[str, Any]] = None):
    return create_app(CONFIG_FILENAME_TEST_ADMIN, config_overrides)


def create_site_app(config_overrides: Optional[Dict[str, Any]] = None):
    return create_app(CONFIG_FILENAME_TEST_SITE, config_overrides)
