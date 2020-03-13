"""
tests.base
~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path

from byceps.application import create_app


_CONFIG_PATH = Path('../config')
CONFIG_FILENAME_TEST_PARTY = _CONFIG_PATH / 'test_party.py'
CONFIG_FILENAME_TEST_ADMIN = _CONFIG_PATH / 'test_admin.py'
