"""
tests.base
~~~~~~~~~~

Base classes for test cases

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from byceps.application import create_app
from byceps.database import db
from byceps.services.authentication.session.models import SessionToken

from testfixtures.authentication import create_session_token
from testfixtures.brand import create_brand
from testfixtures.party import create_party
from testfixtures.user import create_user

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

        self.create_brand_and_party()
        self.create_admin()

    def create_brand_and_party(self):
        self.brand = create_brand()
        db.session.add(self.brand)

        self.party = create_party(brand=self.brand)
        db.session.add(self.party)

        db.session.commit()

    def create_admin(self):
        self.admin = create_user('Admin')

        db.session.add(self.admin)
        db.session.commit()

        session_token = create_session_token(self.admin.id)

        self.db.session.add(session_token)
        self.db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @contextmanager
    def client(self, *, user=None):
        """Provide an HTTP client.

        If a user is given, the client authenticates with the user's
        credentials.
        """
        client = self.app.test_client()

        if user is not None:
            add_user_credentials_to_session(client, user)

        yield client


def add_user_credentials_to_session(client, user):
    session_token = SessionToken.query.filter_by(user_id=user.id).one_or_none()

    with client.session_transaction() as session:
        session['user_id'] = str(user.id)
        session['user_auth_token'] = str(session_token.token)
