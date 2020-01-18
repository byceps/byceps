"""
tests.base
~~~~~~~~~~

Base classes for test cases

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from byceps.application import create_app
from byceps.database import db

from tests.database import set_up_database, tear_down_database
from tests import mocks


_CONFIG_PATH = Path('../config')
CONFIG_FILENAME_TEST_PARTY = _CONFIG_PATH / 'test_party.py'
CONFIG_FILENAME_TEST_ADMIN = _CONFIG_PATH / 'test_admin.py'


class AbstractAppTestCase(TestCase):

    @patch('redis.StrictRedis.from_url', mocks.strict_redis_client_from_url)
    def setUp(self, config_filename=CONFIG_FILENAME_TEST_PARTY):
        self.app = create_app(config_filename)

        # Allow overriding of database URI from the environment.
        db_uri_override = os.environ.get('DATABASE_URI')
        if db_uri_override:
            self.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri_override

        self.db = db
        db.app = self.app

        set_up_database(db)

    def tearDown(self):
        tear_down_database(db)
