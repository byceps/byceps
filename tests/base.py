"""
tests.base
~~~~~~~~~~

Base classes for test cases

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from byceps.application import create_app
from byceps.database import db
from byceps.services.authentication.session.service \
    import find_session_token_for_user

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

        db.reflect()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @contextmanager
    def client(self, *, user_id=None):
        """Provide an HTTP client.

        If a user ID is given, the client authenticates with the user's
        credentials.
        """
        client = self.app.test_client()

        if user_id is not None:
            add_user_credentials_to_session(client, user_id)

        yield client


def add_user_credentials_to_session(client, user_id):
    session_token = find_session_token_for_user(user_id)

    with client.session_transaction() as session:
        session['user_id'] = str(user_id)
        session['user_auth_token'] = str(session_token.token)
